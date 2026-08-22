"""Explainable workplace risk signal scoring."""

from __future__ import annotations

from schemas.models import RiskLevel, RiskSignalResult


def _level(score: float) -> RiskLevel:
    if score >= 0.7:
        return RiskLevel.HIGH
    if score >= 0.4:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def calculate_risk_signal(employee_id: str, metrics: dict) -> RiskSignalResult:
    """Calculate workplace risk signal from structured HR metrics.

    This is a workplace risk signal — NOT a medical or psychological prediction.
    """
    attendance_rate = float(metrics.get("attendance_rate", 0.9))
    late_rate = float(metrics.get("late_rate", 0.0))
    absence_trend = float(metrics.get("absence_trend_delta", 0.0))  # positive = worsening
    leave_days_recent = float(metrics.get("leave_days_recent", 0))
    overtime_delta = float(metrics.get("overtime_delta", 0.0))  # negative = decreased
    workload_indicator = float(metrics.get("workload_indicator", 0.5))  # 0-1

    score = 0.0
    factors: list[str] = []
    reasons: list[str] = []
    recommendations: list[str] = []

    if attendance_rate < 0.85:
        contribution = (0.85 - attendance_rate) * 1.5
        score += contribution
        factors.append(f"Attendance rate: {attendance_rate:.0%}")
        reasons.append(f"Attendance rate at {attendance_rate:.0%} is below team baseline")

    if late_rate > 0.2:
        contribution = min(late_rate, 0.6) * 0.8
        score += contribution
        factors.append(f"Late arrival rate: {late_rate:.0%}")
        reasons.append(f"Late arrival rate of {late_rate:.0%} exceeds normal threshold")

    if absence_trend > 0.1:
        score += min(absence_trend, 0.5) * 0.9
        factors.append(f"Absence trend increase: {absence_trend:.0%}")
        reasons.append(f"Absence frequency increased {absence_trend:.0%} over baseline period")

    if leave_days_recent > 10:
        score += 0.1
        factors.append(f"Recent leave days: {leave_days_recent}")

    if overtime_delta < -0.2:
        score += 0.15
        factors.append(f"Overtime change: {overtime_delta:.0%}")
        reasons.append(f"Overtime hours decreased {abs(overtime_delta):.0%} — possible workload shift")

    if workload_indicator > 0.75:
        score += 0.1
        factors.append(f"Workload indicator: {workload_indicator:.0%}")
        reasons.append("Workload indicators suggest elevated demand")

    score = min(max(score, 0.0), 1.0)
    level = _level(score)

    if level == RiskLevel.HIGH:
        recommendations = [
            "Schedule a supportive HR check-in conversation",
            "Review current workload allocation and team coverage",
            "Monitor attendance pattern over the next 2 weeks",
        ]
    elif level == RiskLevel.MEDIUM:
        recommendations = [
            "Review team dynamics and project assignments",
            "Monitor attendance and leave patterns",
        ]
    else:
        recommendations = ["Maintain current support level; no immediate action required"]

    if not reasons:
        reasons = ["No significant workplace risk signals detected in current data"]

    return RiskSignalResult(
        employee_id=employee_id,
        employee_name=metrics.get("employee_name"),
        risk_score=round(score, 2),
        risk_level=level,
        reasons=reasons,
        recommendations=recommendations,
        supporting_factors=factors,
    )
