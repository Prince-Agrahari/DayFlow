"""Bridge to analytics package (adds analytics/ to Python path)."""

from __future__ import annotations

import sys
from pathlib import Path

_ANALYTICS_ROOT = Path(__file__).resolve().parents[3] / "analytics"


def _ensure_analytics_path() -> None:
    path = str(_ANALYTICS_ROOT)
    if path not in sys.path:
        sys.path.insert(0, path)


def get_dashboard_metrics(data: dict) -> dict:
    _ensure_analytics_path()
    from metrics import get_dashboard_metrics as compute

    return compute(data)


def generate_priority_queue(
    anomalies: list[dict],
    risk_signals: list[dict],
    leave_conflicts: list[dict],
    pending_actions: list[dict],
) -> list[dict]:
    _ensure_analytics_path()
    from priority_queue import generate_priority_queue as compute

    return compute(anomalies, risk_signals, leave_conflicts, pending_actions)


def calculate_team_availability(
    department: str,
    start_date: str,
    end_date: str,
    employees: list[dict],
    leave_records: list[dict],
    attendance_records: list[dict],
) -> dict:
    _ensure_analytics_path()
    from team_availability import calculate_team_availability as compute

    return compute(department, start_date, end_date, employees, leave_records, attendance_records)


def build_report(report_type: str, data: dict) -> dict:
    _ensure_analytics_path()
    from reports import (
        build_attendance_report,
        build_department_report,
        build_leave_report,
        build_payroll_summary,
        build_risk_summary,
    )

    builders = {
        "attendance": lambda: build_attendance_report(data.get("attendance_records", []), data.get("employees", [])),
        "leave": lambda: build_leave_report(data.get("leave_requests", []), data.get("employees", [])),
        "department": lambda: build_department_report(data.get("employees", []), data.get("attendance_records", [])),
        "payroll": lambda: build_payroll_summary(data.get("payroll_records", [])),
        "risk": lambda: build_risk_summary(data.get("risk_signals", []), data.get("anomalies", [])),
    }
    builder = builders.get(report_type)
    if not builder:
        raise ValueError(f"Unknown report type: {report_type}")
    return builder()
