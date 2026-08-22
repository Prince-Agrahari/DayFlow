"""Time-series trend aggregations.

Trends:
- monthly attendance trend
- leave trend
- per-employee attendance/leave trends

Implementation pending — feature/analytics-devops branch.
"""


def get_attendance_trend(records: list[dict], period: str = "monthly") -> list[dict]:
    """Aggregate attendance records into time-series trend."""
    raise NotImplementedError("Implement on feature/analytics-devops branch")


def get_leave_trend(records: list[dict], period: str = "monthly") -> list[dict]:
    """Aggregate leave records into time-series trend."""
    raise NotImplementedError("Implement on feature/analytics-devops branch")
