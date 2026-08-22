"""Analytics orchestration — fetches DB data and delegates to analytics module."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session, joinedload

from app.models.attendance import Attendance
from app.models.employee import EmployeeProfile
from app.models.enums import AttendanceStatus, EmploymentStatus, LeaveStatus
from app.models.leave_request import LeaveBalance, LeaveRequest
from app.models.payroll import Payroll
from app.schemas.analytics import AnalyticsDashboardResponse, DepartmentStat, TeamAvailabilityDay, TeamAvailabilityResponse, TrendPoint
from app.services.ai_bridge import get_engine
from app.services.analytics_bridge import (
    calculate_team_availability,
    generate_priority_queue,
    get_dashboard_metrics,
)


def _employee_dict(profile: EmployeeProfile) -> dict:
    return {
        "id": str(profile.id),
        "employee_id": profile.employee_id,
        "full_name": profile.user.full_name if profile.user else profile.employee_id,
        "department": profile.department,
        "employment_status": profile.employment_status.value,
    }


def _attendance_dict(record: Attendance, employee_id: str) -> dict:
    return {
        "employee_id": employee_id,
        "date": record.date.isoformat(),
        "check_in_time": record.check_in_time.isoformat() if record.check_in_time else None,
        "check_out_time": record.check_out_time.isoformat() if record.check_out_time else None,
        "working_hours": float(record.working_hours or 0),
        "status": record.status.value,
        "is_late": record.is_late,
    }


def _leave_dict(lr: LeaveRequest, employee_id: str, employee_name: str) -> dict:
    return {
        "employee_id": employee_id,
        "employee_name": employee_name,
        "leave_type": lr.leave_type.value,
        "start_date": lr.start_date.isoformat(),
        "end_date": lr.end_date.isoformat(),
        "status": lr.status.value,
        "reason": lr.reason,
    }


def _collect_structured_data(db: Session) -> dict:
    profiles = (
        db.query(EmployeeProfile)
        .options(joinedload(EmployeeProfile.user))
        .filter(EmployeeProfile.employment_status == EmploymentStatus.ACTIVE)
        .all()
    )
    id_to_code = {p.id: p.employee_id for p in profiles}
    name_map = {p.employee_id: (p.user.full_name if p.user else p.employee_id) for p in profiles}

    employees = [_employee_dict(p) for p in profiles]

    attendance_rows = db.query(Attendance).all()
    attendance_records = [_attendance_dict(r, id_to_code.get(r.employee_id, "")) for r in attendance_rows]

    leave_rows = db.query(LeaveRequest).options(joinedload(LeaveRequest.employee).joinedload(EmployeeProfile.user)).all()
    leave_requests = [
        _leave_dict(lr, lr.employee.employee_id, lr.employee.user.full_name if lr.employee and lr.employee.user else "")
        for lr in leave_rows
        if lr.employee
    ]

    payroll_rows = db.query(Payroll).all()
    payroll_records = [
        {
            "employee_id": id_to_code.get(p.employee_id, ""),
            "base_salary": float(p.base_salary),
            "net_salary": float(p.net_salary),
        }
        for p in payroll_rows
    ]

    return {
        "employees": employees,
        "attendance_records": attendance_records,
        "leave_requests": leave_requests,
        "payroll_records": payroll_records,
        "name_map": name_map,
        "today": date.today().isoformat(),
    }


def fetch_attendance_for_ai(db: Session) -> list[dict]:
    data = _collect_structured_data(db)
    enriched = []
    for r in data["attendance_records"]:
        row = dict(r)
        row["employee_name"] = data["name_map"].get(r["employee_id"])
        enriched.append(row)
    return enriched


def compute_risk_signals(db: Session) -> list[dict]:
    data = _collect_structured_data(db)
    engine = get_engine()
    signals = []
    grouped: dict[str, list[dict]] = {}
    for r in data["attendance_records"]:
        grouped.setdefault(r["employee_id"], []).append(r)

    for emp in data["employees"]:
        eid = emp["employee_id"]
        records = grouped.get(eid, [])
        if not records:
            continue
        present = sum(1 for r in records if r["status"] == "PRESENT")
        late = sum(1 for r in records if r.get("is_late"))
        total = len(records)
        metrics = {
            "employee_name": emp["full_name"],
            "attendance_rate": present / total if total else 0.9,
            "late_rate": late / total if total else 0,
            "absence_trend_delta": sum(1 for r in records[-14:] if r["status"] == "ABSENT") / max(min(14, total), 1),
        }
        result = engine.calculate_risk(eid, metrics)
        if result.risk_level.value != "LOW" or result.risk_score >= 0.35:
            signals.append(result.model_dump())
    return signals


def get_dashboard_stats(db: Session) -> AnalyticsDashboardResponse:
    data = _collect_structured_data(db)
    engine = get_engine()
    anomalies = [a.model_dump() for a in engine.detect_anomalies(fetch_attendance_for_ai(db))]
    risk_signals = compute_risk_signals(db)
    data["anomalies"] = anomalies
    data["risk_signals"] = risk_signals

    metrics = get_dashboard_metrics(data)
    return AnalyticsDashboardResponse(
        total_employees=metrics["total_employees"],
        attendance_rate=metrics["attendance_rate"],
        present_today=metrics["present_today"],
        absent_today=metrics["absent_today"],
        on_leave_today=metrics["on_leave_today"],
        pending_leaves=metrics["pending_leaves"],
        department_absenteeism=[DepartmentStat(**d) for d in metrics["department_absenteeism"]],
        monthly_attendance_trend=[TrendPoint(**t) for t in metrics["monthly_attendance_trend"]],
        leave_trend=[TrendPoint(**t) for t in metrics["leave_trend"]],
        payroll_summary=metrics["payroll_summary"],
        risk_distribution=metrics["risk_distribution"],
        anomaly_distribution=metrics["anomaly_distribution"],
    )


def get_team_availability(
    db: Session,
    department: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> TeamAvailabilityResponse:
    today = date.today()
    start = start_date or today.isoformat()
    end = end_date or (today + timedelta(days=6)).isoformat()
    data = _collect_structured_data(db)
    result = calculate_team_availability(
        department,
        start,
        end,
        data["employees"],
        data["leave_requests"],
        data["attendance_records"],
    )
    daily = [
        TeamAvailabilityDay(
            date=row["date"],
            available=row["available"],
            on_leave=row["on_leave"],
            absent=row["absent"],
            availability_rate=row["availability_rate"],
        )
        for row in result["daily_availability"]
    ]
    return TeamAvailabilityResponse(
        department=result["department"],
        start_date=result["start_date"],
        end_date=result["end_date"],
        total_employees=result["total_employees"],
        daily_availability=daily,
    )


def get_priority_queue(db: Session) -> dict:
    data = _collect_structured_data(db)
    engine = get_engine()
    attendance = fetch_attendance_for_ai(db)
    anomalies = [a.model_dump() for a in engine.detect_anomalies(attendance)]
    risk_signals = compute_risk_signals(db)

    leave_conflicts = []
    pending = [lr for lr in data["leave_requests"] if lr["status"] == "PENDING"]
    for lr in pending[:5]:
        req = build_leave_request_from_pending(lr, data)
        rec = engine.recommend_leave(req)
        if rec.conflict_level.value in {"MEDIUM", "HIGH"}:
            leave_conflicts.append(
                {
                    "conflict_level": rec.conflict_level.value,
                    "employee_id": lr["employee_id"],
                    "employee_name": lr["employee_name"],
                    "description": f"Leave conflict for {lr['employee_name']}",
                    "reasons": rec.reasons,
                    "recommendation": rec.recommendation,
                }
            )

    pending_actions = []
    if data["leave_requests"]:
        pending_count = sum(1 for lr in data["leave_requests"] if lr["status"] == "PENDING")
        if pending_count:
            pending_actions.append(
                {
                    "priority": "LOW" if pending_count < 3 else "MEDIUM",
                    "title": "Pending Leave Requests",
                    "description": f"{pending_count} leave request(s) awaiting review",
                    "employee_id": "N/A",
                    "employee_name": "Multiple",
                    "reason": "Administrative backlog",
                    "recommended_action": "Review and respond to pending leave requests",
                }
            )

    dept_conflicts = _team_availability_conflicts(db, data)
    items = generate_priority_queue(anomalies, risk_signals, leave_conflicts + dept_conflicts, pending_actions)
    return {"generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "items": items}


def build_leave_request_from_pending(lr: dict, data: dict):
    from app.services.ai_bridge import build_leave_request

    emp = next((e for e in data["employees"] if e["employee_id"] == lr["employee_id"]), {})
    dept = emp.get("department", "Engineering")
    dept_employees = [e for e in data["employees"] if e["department"] == dept]
    existing = [l for l in data["leave_requests"] if l["status"] == "APPROVED" and l["employee_id"] != lr["employee_id"]]
    team_avail = calculate_team_availability(
        dept,
        lr["start_date"],
        lr["end_date"],
        data["employees"],
        data["leave_requests"],
        data["attendance_records"],
    )
    return build_leave_request(
        {
            "employee_id": lr["employee_id"],
            "employee_name": lr["employee_name"],
            "start_date": lr["start_date"],
            "end_date": lr["end_date"],
            "leave_type": lr["leave_type"],
            "existing_leave": existing,
            "team_availability": team_avail["daily_availability"],
            "department_staffing": {"total_employees": len(dept_employees)},
        }
    )


def _team_availability_conflicts(db: Session, data: dict) -> list[dict]:
    conflicts = []
    departments = {e["department"] for e in data["employees"]}
    today = date.today()
    for dept in departments:
        result = calculate_team_availability(
            dept,
            today.isoformat(),
            (today + timedelta(days=6)).isoformat(),
            data["employees"],
            data["leave_requests"],
            data["attendance_records"],
        )
        low_days = [d for d in result["daily_availability"] if d["availability_rate"] < 0.65]
        if low_days:
            worst = min(low_days, key=lambda x: x["availability_rate"])
            conflicts.append(
                {
                    "conflict_level": "MEDIUM",
                    "employee_id": "N/A",
                    "employee_name": f"{dept} Team",
                    "description": f"Low team availability in {dept} next week",
                    "reasons": [f"Team availability drops to {worst['availability_rate']:.0%} on {worst['date']}"],
                    "recommendation": "Coordinate coverage plan before approving additional leave",
                }
            )
    return conflicts


def build_copilot_context(db: Session) -> dict:
    queue = get_priority_queue(db)
    dashboard = get_dashboard_stats(db)
    return {
        "priority_queue": queue["items"][:5],
        "pending_leaves": [lr for lr in _collect_structured_data(db)["leave_requests"] if lr["status"] == "PENDING"][:10],
        "anomalies": fetch_attendance_for_ai(db)[:5],
        "department_absenteeism": [d.model_dump() for d in dashboard.department_absenteeism],
    }


def build_employee_context(db: Session, profile: EmployeeProfile) -> dict:
    balances = db.query(LeaveBalance).filter(LeaveBalance.employee_id == profile.id).all()
    leaves = db.query(LeaveRequest).filter(LeaveRequest.employee_id == profile.id).all()
    attendance = (
        db.query(Attendance)
        .filter(Attendance.employee_id == profile.id)
        .order_by(Attendance.date.desc())
        .limit(30)
        .all()
    )
    payroll = db.query(Payroll).filter(Payroll.employee_id == profile.id).first()
    present = sum(1 for a in attendance if a.status == AttendanceStatus.PRESENT)
    absent = sum(1 for a in attendance if a.status == AttendanceStatus.ABSENT)
    return {
        "employee_id": profile.employee_id,
        "leave_balances": [
            {"leave_type": b.leave_type.value, "remaining_days": float(b.total_days - b.used_days)}
            for b in balances
        ],
        "leave_requests": [
            {"start_date": lr.start_date.isoformat(), "end_date": lr.end_date.isoformat(), "status": lr.status.value}
            for lr in leaves
        ],
        "attendance_summary": {
            "present": present,
            "absent": absent,
            "rate": f"{round(present / max(len(attendance), 1) * 100)}%",
        },
        "payroll": {
            "net_salary": float(payroll.net_salary) if payroll else 0,
            "currency": payroll.currency if payroll else "USD",
        },
    }
