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
    anomaly: bool
    score: float
    severity: AnomalySeverity
    reason: str


class RiskSignalResult(BaseModel):
    employee_id: str
    risk_score: float = Field(ge=0.0, le=1.0)
    risk_level: RiskLevel
    reasons: list[str]
    recommendations: list[str]


class LeaveRecommendationResult(BaseModel):
    conflict_level: ConflictLevel
    recommendation: str
    reasons: list[str]


class CopilotResponse(BaseModel):
    answer: str
    sources: list[dict]
    structured_data: dict | None = None


class AssistantResponse(BaseModel):
    answer: str
    data_scope: str = "employee_self"
