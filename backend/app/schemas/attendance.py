"""Attendance schemas."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import AttendanceStatus


class CheckInRequest(BaseModel):
    notes: str | None = None


class AttendanceResponse(BaseModel):
    id: int
    employee_id: str
    date: date
    check_in_time: datetime | None = None
    check_out_time: datetime | None = None
    working_hours: Decimal | None = None
    status: AttendanceStatus
    is_late: bool
    notes: str | None = None

    model_config = {"from_attributes": True}


class AttendanceSummary(BaseModel):
    total_days: int
    present: int
    absent: int
    half_day: int = 0
    leave: int = 0
    total_working_hours: float
    late_count: int


class AttendancePeriodResponse(BaseModel):
    period: str
    start_date: date
    end_date: date
    records: list[AttendanceResponse]
    summary: AttendanceSummary


class PaginatedAttendance(BaseModel):
    items: list[AttendanceResponse]
    total: int
    page: int
    page_size: int
