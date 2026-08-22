"""Attendance Anomaly Detection using Isolation Forest.

Analyzes historical attendance for explainable anomalies:
- check-in time, check-out time, working hours
- late frequency, absence frequency

Implementation pending — feature/ai-intelligence branch.
"""

from .schemas import AnomalyResult


def detect_anomalies(attendance_records: list[dict]) -> list[AnomalyResult]:
    """Detect attendance anomalies from structured records.

    Args:
        attendance_records: List of dicts with keys:
            employee_id, date, check_in_time, check_out_time,
            working_hours, is_late, status

    Returns:
        List of AnomalyResult for flagged employees.
    """
    raise NotImplementedError("Implement on feature/ai-intelligence branch")
