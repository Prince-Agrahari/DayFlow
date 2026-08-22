"""AI engine schema validation tests."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "ai-engine"))

from schemas.models import (
    AnomalyResult,
    AnomalySeverity,
    ConflictLevel,
    LeaveRecommendationResult,
    RiskLevel,
    RiskSignalResult,
)


def test_anomaly_result_schema():
    result = AnomalyResult(
        employee_id="EMP001",
        anomaly=True,
        score=-0.42,
        severity=AnomalySeverity.HIGH,
        reason="Unusual check-in pattern detected",
        supporting_factors=["Late arrivals: 4/10 days"],
        recommendation="Review attendance history with the employee.",
    )
    assert result.anomaly is True
    assert result.severity == AnomalySeverity.HIGH
    assert result.supporting_factors


def test_risk_signal_bounds():
    result = RiskSignalResult(
        employee_id="EMP007",
        risk_score=0.78,
        risk_level=RiskLevel.HIGH,
        reasons=["Increased absence frequency"],
        recommendations=["Schedule HR check-in"],
        supporting_factors=["Absence trend increase: 15%"],
    )
    assert 0.0 <= result.risk_score <= 1.0
    assert result.risk_level == RiskLevel.HIGH


def test_leave_recommendation_schema():
    result = LeaveRecommendationResult(
        conflict_level=ConflictLevel.MEDIUM,
        recommendation="Consider approving with coverage plan",
        reasons=["Team availability at 62%"],
        supporting_factors=["Team availability on 2026-01-10: 62%"],
    )
    assert result.conflict_level == ConflictLevel.MEDIUM
