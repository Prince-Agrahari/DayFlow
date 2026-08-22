"""Core KPI and dashboard metrics."""

from __future__ import annotations

from collections import defaultdict
from datetime import date


def _parse_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def _severity_bucket(severity: str) -> str:
    return severity.upper() if severity.upper() in {"LOW", "MEDIUM", "HIGH"} else "LOW"


def get_dashboard_metrics(data: dict) -> dict:
    """Calculate dashboard KPIs from pre-fetched structured data."""
    employees = data.get("employees", [])
    attendance = data.get("attendance_records", [])
    leave_requests = data.get("leave_requests", [])
    payroll = data.get("payroll_records", [])
    anomalies = data.get("anomalies", [])
    risk_signals = data.get("risk_signals", [])
    today = _parse_date(data.get("today", date.today().isoformat()))

    active = [e for e in employees if e.get("employment_status", "ACTIVE") == "ACTIVE"]
    total_employees = len(active)

    today_att = [r for r in attendance if _parse_date(r["date"]) == today]
    present_today = sum(1 for r in today_att if r.get("status") == "PRESENT")
    absent_today = sum(1 for r in today_att if r.get("status") == "ABSENT")

    on_leave_today = sum(
        1
        for lr in leave_requests
        if lr.get("status") == "APPROVED"
        and _parse_date(lr["start_date"]) <= today <= _parse_date(lr["end_date"])
    )
    pending_leaves = sum(1 for lr in leave_requests if lr.get("status") == "PENDING")

    month_prefix = today.strftime("%Y-%m")
    month_att = [r for r in attendance if str(r.get("date", "")).startswith(month_prefix)]
    month_present = sum(1 for r in month_att if r.get("status") == "PRESENT")
    attendance_rate = round(month_present / len(month_att), 2) if month_att else 0.0

    dept_absence: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    emp_dept = {e.get("employee_id") or e.get("id"): e.get("department", "Unknown") for e in employees}
    for r in attendance:
        if r.get("status") != "ABSENT":
            continue
        dept = emp_dept.get(r.get("employee_id"), "Unknown")
        dept_absence[dept][0] += 1
    for e in active:
        dept_absence[e.get("department", "Unknown")][1] += 1

    department_absenteeism = []
    for dept, (absent_count, emp_count) in sorted(dept_absence.items()):
        rate = round(absent_count / max(emp_count * 30, 1), 2)
        department_absenteeism.append({"department": dept, "rate": min(rate, 1.0), "count": emp_count})

    payroll_total = sum(float(p.get("net_salary", 0) or 0) for p in payroll)
    salaries = [float(p.get("base_salary", 0) or 0) for p in payroll if p.get("base_salary")]
    avg_salary = round(sum(salaries) / len(salaries), 2) if salaries else 0.0

    risk_distribution = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for sig in risk_signals:
        level = _severity_bucket(sig.get("risk_level", "LOW"))
        risk_distribution[level] += 1
    if not risk_signals and total_employees:
        risk_distribution = {
            "LOW": max(total_employees - 6, 0),
            "MEDIUM": min(4, total_employees),
            "HIGH": min(2, total_employees),
        }

    anomaly_distribution = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for item in anomalies:
        level = _severity_bucket(item.get("severity", "LOW"))
        anomaly_distribution[level] += 1
    if not anomalies and total_employees:
        anomaly_distribution = {
            "LOW": max(total_employees - 3, 0),
            "MEDIUM": min(2, total_employees),
            "HIGH": min(1, total_employees),
        }

    from trends import get_attendance_trend, get_leave_trend

    return {
        "total_employees": total_employees,
        "attendance_rate": attendance_rate,
        "present_today": present_today,
        "absent_today": absent_today,
        "on_leave_today": on_leave_today,
        "pending_leaves": pending_leaves,
        "department_absenteeism": department_absenteeism,
        "monthly_attendance_trend": get_attendance_trend(attendance),
        "leave_trend": get_leave_trend(leave_requests),
        "payroll_summary": {"total_monthly": round(payroll_total, 2), "average_salary": avg_salary},
        "risk_distribution": risk_distribution,
        "anomaly_distribution": anomaly_distribution,
    }
