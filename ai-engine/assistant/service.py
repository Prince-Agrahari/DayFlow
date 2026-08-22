"""Employee AI Assistant — user-scoped data only."""

from __future__ import annotations

from assistant.prompts import ASSISTANT_SYSTEM_PROMPT
from copilot.gemini_client import GeminiError, call_gemini, structured_context_block
from schemas.models import AssistantResponse


def ask_assistant(
    question: str,
    employee_context: dict,
    *,
    api_key: str,
    model: str = "gemini-2.0-flash",
) -> AssistantResponse:
    user_prompt = f"""Employee Question: {question}

Your Authorized Employee Data (ONLY use this):
{structured_context_block(employee_context)}

Answer based solely on the data above."""

    try:
        answer = call_gemini(api_key=api_key, model=model, system_prompt=ASSISTANT_SYSTEM_PROMPT, user_prompt=user_prompt)
    except GeminiError:
        answer = _fallback_answer(question, employee_context)

    return AssistantResponse(answer=answer, data_scope="employee_self")


def _fallback_answer(question: str, ctx: dict) -> str:
    q = question.lower()
    if "leave" in q and ("how many" in q or "balance" in q):
        balances = ctx.get("leave_balances", [])
        parts = [f"{b.get('leave_type')}: {b.get('remaining_days', b.get('total_days', 0))} days remaining" for b in balances]
        return "Your leave balances:\n" + "\n".join(parts) if parts else "Leave balance data not available."
    if "attendance" in q:
        summary = ctx.get("attendance_summary", {})
        return f"Attendance summary: {summary.get('present', 0)} present, {summary.get('absent', 0)} absent, rate {summary.get('rate', 'N/A')}."
    if "status" in q and "leave" in q:
        leaves = ctx.get("leave_requests", [])
        return "\n".join(f"{l.get('start_date')} to {l.get('end_date')}: {l.get('status')}" for l in leaves) or "No leave requests found."
    if "salary" in q or "pay" in q:
        payroll = ctx.get("payroll", {})
        return f"Net salary: {payroll.get('net_salary', 'N/A')} {payroll.get('currency', 'USD')}."
    return "I can help with your leaves, attendance, leave status, and salary. Please ask a specific question."
