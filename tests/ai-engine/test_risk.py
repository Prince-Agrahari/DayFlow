"""Workplace risk signal tests."""

from schemas.models import RiskLevel
from services.engine import AIEngine


def test_low_risk_default_metrics():
    engine = AIEngine()
    result = engine.calculate_risk("EMP001", {"employee_name": "Jane Doe"})
    assert result.risk_level == RiskLevel.LOW
    assert 0.0 <= result.risk_score <= 1.0
    assert result.reasons
    assert result.recommendations
    assert result.supporting_factors is not None


def test_high_risk_poor_attendance():
    engine = AIEngine()
    result = engine.calculate_risk(
        "EMP003",
        {
            "employee_name": "At Risk",
            "attendance_rate": 0.65,
            "late_rate": 0.45,
            "absence_trend_delta": 0.25,
            "workload_indicator": 0.85,
        },
    )
    assert result.risk_level == RiskLevel.HIGH
    assert result.risk_score >= 0.7
    assert len(result.reasons) >= 2
    assert "Schedule a supportive HR check-in conversation" in result.recommendations[0]


def test_medium_risk_moderate_signals():
    engine = AIEngine()
    result = engine.calculate_risk(
        "EMP004",
        {"attendance_rate": 0.75, "late_rate": 0.35, "absence_trend_delta": 0.05},
    )
    assert result.risk_level == RiskLevel.MEDIUM
    assert result.risk_score >= 0.4
    assert result.supporting_factors
