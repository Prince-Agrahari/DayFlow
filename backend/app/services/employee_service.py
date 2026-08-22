"""Employee management service."""

import uuid
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.security import hash_password
from app.models.department import Department
from app.models.employee import EmployeeProfile
from app.models.enums import ActivityAction, LeaveType, UserRole
from app.models.leave_request import LeaveBalance
from app.models.payroll import Payroll
from app.models.user import User
from app.services.activity_service import log_activity
from app.services.mappers import employee_to_response
from app.schemas.employee import EmployeeAdminUpdate, EmployeeCreate, EmployeeSelfUpdate


def list_employees(
    db: Session,
    *,
    search: str | None = None,
    department: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[EmployeeProfile], int]:
    query = db.query(EmployeeProfile).options(joinedload(EmployeeProfile.user))
    if search:
        like = f"%{search.lower()}%"
        query = query.join(User).filter(
            (EmployeeProfile.employee_id.ilike(like)) | (User.full_name.ilike(like)) | (User.email.ilike(like))
        )
    if department:
        query = query.filter(EmployeeProfile.department == department)
    total = query.count()
    items = query.order_by(EmployeeProfile.employee_id).offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def get_employee(db: Session, identifier: str) -> EmployeeProfile:
    query = db.query(EmployeeProfile).options(joinedload(EmployeeProfile.user))
    if _is_uuid(identifier):
        profile = query.filter(EmployeeProfile.id == uuid.UUID(identifier)).first()
    else:
        profile = query.filter(EmployeeProfile.employee_id == identifier).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return profile


def _is_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


def create_employee(db: Session, payload: EmployeeCreate, actor: User) -> EmployeeProfile:
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
    )
    db.add(user)
    db.flush()

    dept = db.query(Department).filter(Department.name == payload.department).first()
    count = db.query(EmployeeProfile).count()
    profile = EmployeeProfile(
        user_id=user.id,
        employee_id=f"EMP{count + 1:03d}",
        phone=payload.phone,
        address=payload.address,
        department=payload.department,
        department_id=dept.id if dept else None,
        designation=payload.designation,
        joining_date=payload.joining_date,
        employment_status=payload.employment_status,
        salary=payload.salary,
        profile_picture=payload.profile_picture,
    )
    db.add(profile)
    db.flush()

    net = payload.salary * Decimal("0.94")
    db.add(
        Payroll(
            employee_id=profile.id,
            base_salary=payload.salary,
            basic=payload.salary * Decimal("0.65"),
            hra=payload.salary * Decimal("0.18"),
            allowances=payload.salary * Decimal("0.12"),
            deductions=payload.salary * Decimal("0.05"),
            net_salary=net,
        )
    )

    from datetime import date

    year = date.today().year
    for lt, total in [(LeaveType.PAID, 20), (LeaveType.SICK, 10), (LeaveType.UNPAID, 5)]:
        db.add(LeaveBalance(employee_id=profile.id, leave_type=lt, total_days=total, used_days=0, year=year))

    log_activity(db, user_id=actor.id, action=ActivityAction.EMPLOYEE_CREATED, description=f"Created employee {profile.employee_id}", entity_type="employee", entity_id=profile.employee_id)
    db.commit()
    db.refresh(profile)
    return profile


def update_employee_self(db: Session, profile: EmployeeProfile, payload: EmployeeSelfUpdate, actor: User) -> EmployeeProfile:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    log_activity(db, user_id=actor.id, action=ActivityAction.PROFILE_UPDATED, description="Employee updated own profile", entity_type="employee", entity_id=profile.employee_id)
    db.commit()
    db.refresh(profile)
    return profile


def update_employee_admin(db: Session, profile: EmployeeProfile, payload: EmployeeAdminUpdate, actor: User) -> EmployeeProfile:
    data = payload.model_dump(exclude_unset=True)
    if "full_name" in data:
        profile.user.full_name = data.pop("full_name")
    for field, value in data.items():
        setattr(profile, field, value)
    log_activity(db, user_id=actor.id, action=ActivityAction.PROFILE_UPDATED, description=f"Admin updated employee {profile.employee_id}", entity_type="employee", entity_id=profile.employee_id)
    db.commit()
    db.refresh(profile)
    return profile


def delete_employee(db: Session, profile: EmployeeProfile, actor: User) -> None:
    if profile.user.role == UserRole.ADMIN:
        admin_count = db.query(User).filter(User.role == UserRole.ADMIN).count()
        if admin_count <= 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete the only admin")
    emp_id = profile.employee_id
    db.delete(profile.user)
    log_activity(db, user_id=actor.id, action=ActivityAction.EMPLOYEE_DELETED, description=f"Deleted employee {emp_id}", entity_type="employee", entity_id=emp_id)
    db.commit()


def get_employee_360(db: Session, identifier: str) -> dict:
    """Build Employee 360 view with attendance, leave, AI signals."""
    from collections import defaultdict
    from datetime import date, timedelta

    from app.models.attendance import Attendance
    from app.models.enums import AttendanceStatus, LeaveStatus
    from app.models.leave_request import LeaveRequest
    from app.services.ai_bridge import get_engine
    from app.services.analytics_service import fetch_attendance_for_ai

    profile = get_employee(db, identifier)
    records = (
        db.query(Attendance)
        .filter(Attendance.employee_id == profile.id)
        .order_by(Attendance.date.desc())
        .limit(90)
        .all()
    )

    weekly: dict[str, dict] = defaultdict(lambda: {"present": 0, "absent": 0, "hours": 0.0, "count": 0})
    late_count = 0
    total_hours = 0.0
    present_count = 0
    for r in records:
        week = r.date.strftime("%Y-W%W")
        if r.status == AttendanceStatus.PRESENT:
            weekly[week]["present"] += 1
            present_count += 1
            hrs = float(r.working_hours or 0)
            weekly[week]["hours"] += hrs
            weekly[week]["count"] += 1
            total_hours += hrs
            if r.is_late:
                late_count += 1
        elif r.status == AttendanceStatus.ABSENT:
            weekly[week]["absent"] += 1

    attendance_trend = [
        {
            "week": w,
            "present_days": v["present"],
            "absent_days": v["absent"],
            "avg_hours": round(v["hours"] / max(v["count"], 1), 1),
        }
        for w, v in sorted(weekly.items())[-8:]
    ]

    leaves = db.query(LeaveRequest).filter(LeaveRequest.employee_id == profile.id, LeaveRequest.status == LeaveStatus.APPROVED).all()
    monthly_leave: dict[str, dict] = defaultdict(lambda: {"days": 0, "types": defaultdict(int)})
    for lr in leaves:
        month = lr.start_date.strftime("%Y-%m")
        days = (lr.end_date - lr.start_date).days + 1
        monthly_leave[month]["days"] += days
        monthly_leave[month]["types"][lr.leave_type.value] += days

    leave_trend = [
        {"month": m, "days_taken": v["days"], "type_breakdown": dict(v["types"])}
        for m, v in sorted(monthly_leave.items())[-6:]
    ]

    total_days = len(records) or 1
    working_hours_summary = {
        "avg_daily_hours": round(total_hours / max(present_count, 1), 1),
        "total_overtime_hours": round(max(total_hours - present_count * 8, 0), 1),
        "late_arrival_rate": round(late_count / total_days, 2),
    }

    emp_records = [r for r in fetch_attendance_for_ai(db) if r.get("employee_id") == profile.employee_id]
    engine = get_engine()
    anomalies_raw = engine.detect_anomalies(emp_records) if len(emp_records) >= 5 else []
    anomalies = [
        {
            "employee_id": a.employee_id,
            "employee_name": a.employee_name or profile.user.full_name,
            "anomaly": a.anomaly,
            "score": a.score,
            "severity": a.severity.value,
            "reason": a.reason,
        }
        for a in anomalies_raw
    ]

    metrics = {
        "employee_name": profile.user.full_name,
        "attendance_rate": present_count / total_days,
        "late_rate": late_count / total_days,
        "absence_trend_delta": sum(1 for r in records[:14] if r.status == AttendanceStatus.ABSENT) / max(min(14, total_days), 1),
    }
    risk = engine.calculate_risk(profile.employee_id, metrics)
    risk_signals = None
    if risk.risk_level.value != "LOW" or risk.risk_score >= 0.35:
        risk_signals = {
            "employee_id": profile.employee_id,
            "employee_name": profile.user.full_name,
            "risk_score": risk.risk_score,
            "risk_level": risk.risk_level.value,
            "reasons": risk.reasons,
            "recommendations": risk.recommendations,
        }

    recommendations = list(risk.recommendations[:2]) if risk.recommendations else []
    for a in anomalies_raw[:1]:
        if a.recommendation and a.recommendation not in recommendations:
            recommendations.append(a.recommendation)
    if not recommendations:
        recommendations = ["No immediate HR action required — continue monitoring."]

    return {
        "profile": employee_to_response(profile),
        "attendance_trend": attendance_trend,
        "leave_trend": leave_trend,
        "working_hours_summary": working_hours_summary,
        "anomalies": anomalies,
        "risk_signals": risk_signals,
        "recommendations": recommendations,
    }
