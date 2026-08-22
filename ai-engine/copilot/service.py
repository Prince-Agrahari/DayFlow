"""HR AI Copilot powered by Gemini."""

from __future__ import annotations

from copilot.gemini_client import GeminiError, call_gemini, structured_context_block
from copilot.prompts import COPILOT_SYSTEM_PROMPT
from schemas.models import CopilotResponse


def ask_copilot(
    question: str,
    structured_context: dict,
    *,
    api_key: str,
    model: str = "gemini-2.0-flash",
) -> CopilotResponse:
    user_prompt = f"""HR Question: {question}

Structured HR Data (use ONLY this data):
{structured_context_block(structured_context)}

Provide a clear, actionable answer for HR. Reference specific data points."""

    try:
        answer = call_gemini(api_key=api_key, model=model, system_prompt=COPILOT_SYSTEM_PROMPT, user_prompt=user_prompt)
    except GeminiError:
        answer = _fallback_answer(question, structured_context)

    sources = []
    for key in ("priority_queue", "anomalies", "pending_leaves", "department_absenteeism"):
        if key in structured_context:
            val = structured_context[key]
            count = len(val) if isinstance(val, list) else 1
            sources.append({"type": key, "count": count})

    return CopilotResponse(answer=answer, sources=sources, structured_data=structured_context)


def _fallback_answer(question: str, context: dict) -> str:
    q = question.lower()
    if "attention" in q or "priorit" in q:
        items = context.get("priority_queue", [])
        pending = context.get("pending_leaves", [])
        return (
            f"Based on available HR data: {len(items)} priority item(s) and {len(pending)} pending leave request(s) require review. "
            "Configure GEMINI_API_KEY for detailed AI analysis."
        )
    if "anomal" in q or "unusual" in q:
        anomalies = context.get("anomalies", [])
        return f"{len(anomalies)} attendance anomaly signal(s) detected in current data. Review flagged employees in the HR dashboard."
    if "absenteeism" in q or "department" in q:
        depts = context.get("department_absenteeism", [])
        if depts:
            top = max(depts, key=lambda d: d.get("rate", 0))
            return f"Highest absenteeism: {top.get('department', 'Unknown')} at {top.get('rate', 0):.0%}."
        return "Department absenteeism data not available in current context."
    return "HR Copilot is available. Configure GEMINI_API_KEY for full AI-powered responses. Review structured HR data in the dashboard."
