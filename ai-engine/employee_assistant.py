"""Employee AI Assistant — Gemini-powered self-service helper.

Only returns data scoped to the authenticated employee.

Implementation pending — feature/ai-intelligence branch.
"""

from .schemas import AssistantResponse


def ask_assistant(question: str, employee_context: dict, api_key: str) -> AssistantResponse:
    """Answer employee questions using Gemini with user-scoped data.

    Args:
        question: Natural language employee question
        employee_context: Pre-fetched data for this employee only
        api_key: Gemini API key (server-side only)

    Returns:
        AssistantResponse with answer from authorized data only.
    """
    raise NotImplementedError("Implement on feature/ai-intelligence branch")
