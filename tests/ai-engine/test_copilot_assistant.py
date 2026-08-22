"""Gemini copilot and assistant tests."""

from unittest.mock import patch

from copilot.gemini_client import GeminiError
from services.engine import AIEngine


def test_copilot_gemini_failure_fallback():
    engine = AIEngine(gemini_api_key="")
    context = {
        "priority_queue": [{"employee_id": "EMP002", "reason": "Anomaly"}],
        "pending_leaves": [{"id": "LR1"}],
        "anomalies": [{"employee_id": "EMP002"}],
        "department_absenteeism": [{"department": "Engineering", "rate": 0.18}],
    }
    result = engine.ask_copilot("Who needs attention today?", context)
    assert "priority" in result.answer.lower() or "pending" in result.answer.lower()
    assert result.sources


def test_copilot_gemini_error_uses_fallback():
    engine = AIEngine(gemini_api_key="test-key")
    with patch("copilot.service.call_gemini", side_effect=GeminiError("API down")):
        result = engine.ask_copilot(
            "Which employees have unusual attendance?",
            {"anomalies": [{"employee_id": "EMP002"}]},
        )
    assert "anomaly" in result.answer.lower() or "attendance" in result.answer.lower()


def test_assistant_self_scoped_fallback():
    engine = AIEngine(gemini_api_key="")
    ctx = {
        "employee_id": "EMP001",
        "leave_balances": [{"leave_type": "PAID", "remaining_days": 8}],
        "attendance_summary": {"present": 18, "absent": 2, "rate": "90%"},
        "payroll": {"net_salary": 5200, "currency": "USD"},
    }
    result = engine.ask_assistant("How many leaves do I have?", ctx)
    assert "8" in result.answer
    assert result.data_scope == "employee_self"


def test_assistant_gemini_failure_salary_fallback():
    engine = AIEngine(gemini_api_key="test-key")
    with patch("assistant.service.call_gemini", side_effect=GeminiError("quota")):
        result = engine.ask_assistant(
            "What is my salary?",
            {"payroll": {"net_salary": 4800, "currency": "USD"}},
        )
    assert "4800" in result.answer
