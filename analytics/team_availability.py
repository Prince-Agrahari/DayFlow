"""Team availability analysis for leave planning and heatmaps."""

from __future__ import annotations

from datetime import date, timedelta


def _parse_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def _date_range(start: date, end: date) -> list[date]:
    days = []
    current = start
    while current <= end:
        days.append(current)
        current += timedelta(days=1)
    return days


def calculate_team_availability(
    department: str,
    start_date: str,
    end_date: str,
    employees: list[dict],
    leave_records: list[dict],
    attendance_records: list[dict],
) -> dict:
    """Calculate daily team availability for a department."""
    start = _parse_date(start_date)
    end = _parse_date(end_date)
    dept_employees = [e for e in employees if e.get("department") == department and e.get("employment_status", "ACTIVE") == "ACTIVE"]
    total = len(dept_employees) or 1
    emp_ids = {e.get("employee_id") or e.get("id") for e in dept_employees}

    daily = []
    staffing_conflicts = []

    for d in _date_range(start, end):
        ds = d.isoformat()
        on_leave = sum(
            1
            for lr in leave_records
            if lr.get("employee_id") in emp_ids
            and lr.get("status") == "APPROVED"
            and _parse_date(lr["start_date"]) <= d <= _parse_date(lr["end_date"])
        )
        absent = sum(
            1
            for r in attendance_records
            if r.get("employee_id") in emp_ids
            and _parse_date(r["date"]) == d
            and r.get("status") == "ABSENT"
        )
        available = max(total - on_leave - absent, 0)
        rate = round(available / total, 2)
        daily.append(
            {
                "date": ds,
                "available": available,
                "on_leave": on_leave,
                "absent": absent,
                "availability_rate": rate,
                "department_capacity": total,
                "present_employees": available,
                "staffing_conflict": rate < 0.6,
            }
        )
        if rate < 0.6:
            staffing_conflicts.append({"date": ds, "availability_rate": rate, "department": department})

    return {
        "department": department,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "total_employees": total,
        "department_capacity": total,
        "daily_availability": daily,
        "staffing_conflicts": staffing_conflicts,
        "heatmap": [
            {"date": row["date"], "value": row["availability_rate"], "label": f"{int(row['availability_rate'] * 100)}%"}
            for row in daily
        ],
    }
