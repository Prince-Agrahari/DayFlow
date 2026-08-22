"""Leave schemas."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.models.enums import LeaveStatus, LeaveType


class LeaveCreateRequest(BaseModel):
    leave_type: LeaveType
    start_date: date
    end_date: date
    reason: str = Field(min_length=3, max_length=1000)

    @model_validator(mode="after")
    def validate_dates(self) -> "LeaveCreateRequest":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class LeaveActionRequest(BaseModel):
    comment: str = Field(min_length=1, max_length=1000)


class LeaveResponse(BaseModel):
    id: int
    employee_id: str
    employee_name: str | None = None
    leave_type: LeaveType
    start_date: date
    end_date: date
    reason: str
    status: LeaveStatus
    admin_comment: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class LeaveBalanceResponse(BaseModel):
    leave_type: LeaveType
    total_days: float
    used_days: float
    remaining_days: float


class PaginatedLeaves(BaseModel):
    items: list[LeaveResponse]
    total: int
    page: int
    page_size: int
