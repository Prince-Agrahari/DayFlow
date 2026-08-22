"""AI integration contract — modular stubs for ai-engine module.

Do NOT implement Gemini or ML here. These interfaces define the backend boundary
for Dev 3 (feature/ai-intelligence) to plug in real implementations.
"""

from abc import ABC, abstractmethod

from app.schemas.ai import (
    AnomalyItem,
    AssistantResponse,
    CopilotResponse,
    LeaveRecommendationResponse,
    RiskSignalItem,
)


class AIEngineContract(ABC):
    @abstractmethod
    def detect_attendance_anomalies(self, context: dict) -> list[AnomalyItem]:
        """Analyze structured attendance data for anomalies."""

    @abstractmethod
    def calculate_risk_signals(self, context: dict) -> list[RiskSignalItem]:
        """Calculate workplace risk signals from structured employee metrics."""

    @abstractmethod
    def recommend_leave(self, context: dict) -> LeaveRecommendationResponse:
        """Generate smart leave recommendation from team context."""

    @abstractmethod
    def ask_copilot(self, question: str, context: dict) -> CopilotResponse:
        """HR copilot — structured data injection only, no SQL generation."""

    @abstractmethod
    def ask_assistant(self, question: str, employee_context: dict) -> AssistantResponse:
        """Employee assistant — user-scoped data only."""


class StubAIEngine(AIEngineContract):
    """Placeholder until ai-engine module is integrated."""

    def detect_attendance_anomalies(self, context: dict) -> list[AnomalyItem]:
        return []

    def calculate_risk_signals(self, context: dict) -> list[RiskSignalItem]:
        return []

    def recommend_leave(self, context: dict) -> LeaveRecommendationResponse:
        return LeaveRecommendationResponse(
            conflict_level="LOW",
            recommendation="AI engine not yet integrated — HR should review manually.",
            reasons=["AI module pending integration on feature/ai-intelligence"],
        )

    def ask_copilot(self, question: str, context: dict) -> CopilotResponse:
        return CopilotResponse(
            answer="HR AI Copilot is not yet connected. Please integrate ai-engine/copilot.py.",
            sources=[{"type": "stub", "count": 0}],
            structured_data=context,
        )

    def ask_assistant(self, question: str, employee_context: dict) -> AssistantResponse:
        return AssistantResponse(
            answer="Employee AI Assistant is not yet connected. Please integrate ai-engine/employee_assistant.py.",
            data_scope="employee_self",
        )


def get_ai_engine() -> AIEngineContract:
    """Factory — swap StubAIEngine for real implementation when ai-engine is ready."""
    return StubAIEngine()
