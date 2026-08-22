"""Shared AI response schemas."""

from enum import Enum

from pydantic import BaseModel, Field


class AnomalySeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ConflictLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class AnomalyResult(BaseModel):
    employee_id: str
    employee_name: str | None = None
    anomaly: bool
    score: float
    severity: AnomalySeverity
    reason: str
    supporting_factors: list[str] = Field(default_factory=list)
    recommendation: str = ""


class RiskSignalResult(BaseModel):
    employee_id: str
    employee_name: str | None = None
    risk_score: float = Field(ge=0.0, le=1.0)
    risk_level: RiskLevel
    reasons: list[str]
    recommendations: list[str]
    supporting_factors: list[str] = Field(default_factory=list)


class LeaveRecommendationResult(BaseModel):
    conflict_level: ConflictLevel
    recommendation: str
    reasons: list[str]
    supporting_factors: list[str] = Field(default_factory=list)


class CopilotResponse(BaseModel):
    answer: str
    sources: list[dict]
    structured_data: dict | None = None


class AssistantResponse(BaseModel):
    answer: str
    data_scope: str = "employee_self"


class AnomalyBatchRequest(BaseModel):
    attendance_records: list[dict]


class LeaveRecommendationRequest(BaseModel):
    employee_id: str
    employee_name: str | None = None
    start_date: str
    end_date: str
    leave_type: str
    leave_balances: list[dict] = Field(default_factory=list)
    team_availability: list[dict] = Field(default_factory=list)
    existing_leave: list[dict] = Field(default_factory=list)
    department_staffing: dict = Field(default_factory=dict)


class CopilotRequest(BaseModel):
    question: str


class AssistantRequest(BaseModel):
    question: str
    employee_context: dict
