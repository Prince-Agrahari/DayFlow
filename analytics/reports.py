"""Report-ready data aggregations for HR exports."""

from __future__ import annotations

from collections import defaultdict
from datetime import date


def _parse_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def build_attendance_report(attendance_records: list[dict], employees: list[dict]) -> dict:
    emp_names = {e.get("employee_id"): e.get("full_name", e.get("employee_name", "")) for e in employees}
    by_employee: dict[str, dict] = defaultdict(lambda: {"present": 0, "absent": 0, "late": 0, "total_hours": 0.0})

    for r in attendance_records:
        eid = r.get("employee_id", "unknown")
        bucket = by_employee[eid]
        if r.get("status") == "PRESENT":
            bucket["present"] += 1
            bucket["total_hours"] += float(r.get("working_hours") or 0)
        elif r.get("status") == "ABSENT":
            bucket["absent"] += 1
        if r.get("is_late"):
            bucket["late"] += 1

    rows = []
    for eid, stats in sorted(by_employee.items()):
        total = stats["present"] + stats["absent"]
        rows.append(
            {
                "employee_id": eid,
                "employee_name": emp_names.get(eid, eid),
                "present_days": stats["present"],
                "absent_days": stats["absent"],
                "late_count": stats["late"],
                "attendance_rate": round(stats["present"] / total, 2) if total else 0.0,
                "avg_working_hours": round(stats["total_hours"] / max(stats["present"], 1), 2),
            }
        )
    return {"report_type": "attendance", "generated_at": date.today().isoformat(), "rows": rows}


def build_leave_report(leave_requests: list[dict], employees: list[dict]) -> dict:
    emp_names = {e.get("employee_id"): e.get("full_name", "") for e in employees}
    rows = []
    for lr in leave_requests:
        start = _parse_date(lr["start_date"])
        end = _parse_date(lr["end_date"])
        rows.append(
            {
                "employee_id": lr.get("employee_id"),
                "employee_name": lr.get("employee_name") or emp_names.get(lr.get("employee_id"), ""),
                "leave_type": lr.get("leave_type"),
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "days": (end - start).days + 1,
                "status": lr.get("status"),
                "reason": lr.get("reason", ""),
            }
        )
    return {"report_type": "leave", "generated_at": date.today().isoformat(), "rows": rows}


def build_department_report(employees: list[dict], attendance_records: list[dict]) -> dict:
    dept_stats: dict[str, dict] = defaultdict(lambda: {"employees": 0, "absent": 0, "present": 0})
    emp_dept = {e.get("employee_id"): e.get("department", "Unknown") for e in employees}

    for e in employees:
        if e.get("employment_status", "ACTIVE") == "ACTIVE":
            dept_stats[e.get("department", "Unknown")]["employees"] += 1

    for r in attendance_records:
        dept = emp_dept.get(r.get("employee_id"), "Unknown")
        if r.get("status") == "ABSENT":
            dept_stats[dept]["absent"] += 1
        elif r.get("status") == "PRESENT":
            dept_stats[dept]["present"] += 1

    rows = []
    for dept, stats in sorted(dept_stats.items()):
        total = stats["present"] + stats["absent"]
        rows.append(
            {
                "department": dept,
                "headcount": stats["employees"],
                "absenteeism_rate": round(stats["absent"] / total, 2) if total else 0.0,
                "attendance_rate": round(stats["present"] / total, 2) if total else 0.0,
            }
        )
    return {"report_type": "department", "generated_at": date.today().isoformat(), "rows": rows}


def build_payroll_summary(payroll_records: list[dict]) -> dict:
    total = sum(float(p.get("net_salary", 0) or 0) for p in payroll_records)
    salaries = [float(p.get("base_salary", 0) or 0) for p in payroll_records]
    return {
        "report_type": "payroll",
        "generated_at": date.today().isoformat(),
        "total_monthly": round(total, 2),
        "average_salary": round(sum(salaries) / len(salaries), 2) if salaries else 0.0,
        "employee_count": len(payroll_records),
    }


def build_risk_summary(risk_signals: list[dict], anomalies: list[dict]) -> dict:
    risk_by_level = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for sig in risk_signals:
        level = str(sig.get("risk_level", "LOW")).upper()
        if level in risk_by_level:
            risk_by_level[level] += 1

    anomaly_by_level = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for item in anomalies:
        level = str(item.get("severity", "LOW")).upper()
        if level in anomaly_by_level:
            anomaly_by_level[level] += 1

    return {
        "report_type": "risk_summary",
        "generated_at": date.today().isoformat(),
        "risk_distribution": risk_by_level,
        "anomaly_distribution": anomaly_by_level,
        "flagged_employees": len({s.get("employee_id") for s in risk_signals} | {a.get("employee_id") for a in anomalies}),
    }
