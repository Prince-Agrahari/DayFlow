"""Analytics API contract schemas (data aggregation stubs)."""

from pydantic import BaseModel


class DepartmentStat(BaseModel):
    department: str
    rate: float
    count: int | None = None


class TrendPoint(BaseModel):
    month: str
    rate: float | None = None
    count: int | None = None


class AnalyticsDashboardResponse(BaseModel):
    total_employees: int
    attendance_rate: float
    present_today: int
    absent_today: int
    on_leave_today: int
    pending_leaves: int
    department_absenteeism: list[DepartmentStat]
    monthly_attendance_trend: list[TrendPoint]
    leave_trend: list[TrendPoint]
    payroll_summary: dict[str, float]
    risk_distribution: dict[str, int]
    anomaly_distribution: dict[str, int]


class TeamAvailabilityDay(BaseModel):
    date: str
    available: int
    on_leave: int
    absent: int
    availability_rate: float


class TeamAvailabilityResponse(BaseModel):
    department: str
    start_date: str
    end_date: str
    total_employees: int
    daily_availability: list[TeamAvailabilityDay]
