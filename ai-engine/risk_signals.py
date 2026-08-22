"""Workplace Risk Signal — explainable composite scoring.

Uses attendance trend, late arrivals, absence trend,
leave pattern, overtime, and workload indicators.

Does NOT make medical or psychological predictions.

Implementation pending — feature/ai-intelligence branch.
"""

from .schemas import RiskSignalResult


def calculate_risk_signals(employee_data: dict) -> RiskSignalResult:
    """Calculate workplace risk signal for a single employee.

    Args:
        employee_data: Structured dict with attendance, leave, overtime metrics.

    Returns:
        RiskSignalResult with explainable reasons and HR recommendations.
    """
    raise NotImplementedError("Implement on feature/ai-intelligence branch")
