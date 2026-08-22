"""Analytics package public API."""

from metrics import get_dashboard_metrics
from priority_queue import generate_priority_queue
from reports import (
    build_attendance_report,
    build_department_report,
    build_leave_report,
    build_payroll_summary,
    build_risk_summary,
)
from team_availability import calculate_team_availability
from trends import get_attendance_trend, get_leave_trend

__all__ = [
    "get_dashboard_metrics",
    "get_attendance_trend",
    "get_leave_trend",
    "generate_priority_queue",
    "calculate_team_availability",
    "build_attendance_report",
    "build_leave_report",
    "build_department_report",
    "build_payroll_summary",
    "build_risk_summary",
]

__version__ = "0.1.0"
