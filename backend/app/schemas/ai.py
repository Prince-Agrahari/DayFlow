"""Backend AI request/response schemas."""

from pydantic import BaseModel, Field


class AnomalyRequest(BaseModel):
    attendance_records: list[dict] = Field(default_factory=list)


class AnomalyResponse(BaseModel):
    items: list[dict]


class LeaveRecommendationBody(BaseModel):
    employee_id: str
    employee_name: str | None = None
    start_date: str
    end_date: str
    leave_type: str
    leave_balances: list[dict] = Field(default_factory=list)
    team_availability: list[dict] = Field(default_factory=list)
    existing_leave: list[dict] = Field(default_factory=list)
    department_staffing: dict = Field(default_factory=dict)


class CopilotBody(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    structured_context: dict = Field(default_factory=dict)


class AssistantBody(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    employee_context: dict | None = None
