"""AI engine schema validation tests."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "ai-engine"))

# Import directly from schemas module (ai-engine is on sys.path)
import importlib.util
spec = importlib.util.spec_from_file_location(
    "schemas",
    os.path.join(os.path.dirname(__file__), "..", "..", "ai-engine", "schemas.py"),
)
schemas = importlib.util.module_from_spec(spec)
spec.loader.exec_module(schemas)

AnomalyResult = schemas.AnomalyResult
AnomalySeverity = schemas.AnomalySeverity
RiskSignalResult = schemas.RiskSignalResult
RiskLevel = schemas.RiskLevel
LeaveRecommendationResult = schemas.LeaveRecommendationResult
ConflictLevel = schemas.ConflictLevel


def test_anomaly_result_schema():
    result = AnomalyResult(
        employee_id="EMP001",
        anomaly=True,
        score=-0.42,
        severity=AnomalySeverity.HIGH,
        reason="Unusual check-in pattern detected",
    )
    assert result.anomaly is True
    assert result.severity == AnomalySeverity.HIGH


def test_risk_signal_bounds():
    result = RiskSignalResult(
        employee_id="EMP007",
        risk_score=0.78,
        risk_level=RiskLevel.HIGH,
        reasons=["Increased absence frequency"],
        recommendations=["Schedule HR check-in"],
    )
    assert 0.0 <= result.risk_score <= 1.0
    assert result.risk_level == RiskLevel.HIGH


def test_leave_recommendation_schema():
    result = LeaveRecommendationResult(
        conflict_level=ConflictLevel.MEDIUM,
        recommendation="Consider approving with coverage plan",
        reasons=["Team availability at 62%"],
    )
    assert result.conflict_level == ConflictLevel.MEDIUM
