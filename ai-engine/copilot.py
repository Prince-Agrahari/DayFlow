"""HR AI Copilot — Gemini-powered HR assistant.

Uses controlled structured application data.
Does NOT allow unrestricted SQL generation.

Implementation pending — feature/ai-intelligence branch.
"""

from .schemas import CopilotResponse


def ask_copilot(question: str, structured_context: dict, api_key: str) -> CopilotResponse:
    """Answer HR questions using Gemini with injected structured data.

    Args:
        question: Natural language HR question
        structured_context: Pre-aggregated data (priority queue, leaves, anomalies)
        api_key: Gemini API key (server-side only)

    Returns:
        CopilotResponse with answer and source citations.
    """
    raise NotImplementedError("Implement on feature/ai-intelligence branch")
