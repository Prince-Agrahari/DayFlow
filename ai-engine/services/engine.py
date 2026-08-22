"""Unified AI engine facade."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from schemas.models import (
        AnomalyResult,
        AssistantResponse,
        CopilotResponse,
        LeaveRecommendationRequest,
        LeaveRecommendationResult,
        RiskSignalResult,
    )


class AIEngine:
    """Main entry point for DayFlow AI capabilities."""

    def __init__(self, *, gemini_api_key: str = "", gemini_model: str = "gemini-2.0-flash") -> None:
        self.gemini_api_key = gemini_api_key
        self.gemini_model = gemini_model

    def detect_anomalies(self, attendance_records: list[dict]) -> list["AnomalyResult"]:
        from anomaly.detector import detect_anomalies
        return detect_anomalies(attendance_records)

    def calculate_risk(self, employee_id: str, metrics: dict) -> "RiskSignalResult":
        from risk.calculator import calculate_risk_signal
        return calculate_risk_signal(employee_id, metrics)

    def recommend_leave(self, request: "LeaveRecommendationRequest") -> "LeaveRecommendationResult":
        from leave.recommender import recommend_leave
        return recommend_leave(request)

    def ask_copilot(self, question: str, structured_context: dict) -> "CopilotResponse":
        from copilot.service import ask_copilot
        return ask_copilot(question, structured_context, api_key=self.gemini_api_key, model=self.gemini_model)

    def ask_assistant(self, question: str, employee_context: dict) -> "AssistantResponse":
        from assistant.service import ask_assistant
        return ask_assistant(question, employee_context, api_key=self.gemini_api_key, model=self.gemini_model)
