"""Employee profile schemas."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import EmploymentStatus, UserRole


class EmployeeBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: str | None = None
    address: str | None = None
    department: str
    designation: str
    joining_date: date
    employment_status: EmploymentStatus = EmploymentStatus.ACTIVE
    salary: Decimal = Field(default=Decimal("0"))
    profile_picture: str | None = None


class EmployeeCreate(EmployeeBase):
    password: str = Field(min_length=6, max_length=128)
    role: UserRole = UserRole.EMPLOYEE


class EmployeeSelfUpdate(BaseModel):
    phone: str | None = None
    address: str | None = None
    profile_picture: str | None = None


class EmployeeAdminUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    address: str | None = None
    department: str | None = None
    designation: str | None = None
    employment_status: EmploymentStatus | None = None
    salary: Decimal | None = None
    profile_picture: str | None = None


class EmployeeResponse(BaseModel):
    id: UUID
    employee_id: str
    full_name: str
    email: EmailStr
    phone: str | None = None
    address: str | None = None
    department: str
    designation: str
    joining_date: date
    employment_status: EmploymentStatus
    salary: Decimal
    profile_picture: str | None = None
    role: UserRole

    model_config = {"from_attributes": True}


class PaginatedEmployees(BaseModel):
    items: list[EmployeeResponse]
    total: int
    page: int
    page_size: int


class AttendanceTrendWeek(BaseModel):
    week: str
    present_days: int
    absent_days: int
    avg_hours: float


class LeaveTrendMonth(BaseModel):
    month: str
    days_taken: int
    type_breakdown: dict[str, int]


class WorkingHoursSummary(BaseModel):
    avg_daily_hours: float
    total_overtime_hours: float
    late_arrival_rate: float


class Employee360Response(BaseModel):
    profile: EmployeeResponse
    attendance_trend: list[AttendanceTrendWeek]
    leave_trend: list[LeaveTrendMonth]
    working_hours_summary: WorkingHoursSummary
    anomalies: list[dict]
    risk_signals: dict | None
    recommendations: list[str]
