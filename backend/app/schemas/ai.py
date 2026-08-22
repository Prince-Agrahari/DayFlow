"""AI API contract schemas (integration stubs)."""

from pydantic import BaseModel, Field

from app.models.enums import UserRole


class AnomalyItem(BaseModel):
    employee_id: str
    employee_name: str
    anomaly: bool
    score: float
    severity: str
    reason: str


class RiskSignalItem(BaseModel):
    employee_id: str
    employee_name: str
    risk_score: float
    risk_level: str
    reasons: list[str]
    recommendations: list[str]


class LeaveRecommendationRequest(BaseModel):
    employee_id: str
    start_date: str
    end_date: str
    leave_type: str


class LeaveRecommendationResponse(BaseModel):
    conflict_level: str
    recommendation: str
    reasons: list[str]


class CopilotRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)


class CopilotResponse(BaseModel):
    answer: str
    sources: list[dict]
    structured_data: dict | None = None


class AssistantRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)


class AssistantResponse(BaseModel):
    answer: str
    data_scope: str = "employee_self"
