"""Smart leave recommendation tests."""

from schemas.models import ConflictLevel, LeaveRecommendationRequest
from services.engine import AIEngine


def test_low_conflict_leave():
    engine = AIEngine()
    request = LeaveRecommendationRequest(
        employee_id="EMP001",
        start_date="2026-03-10",
        end_date="2026-03-12",
        leave_type="PAID",
        leave_balances=[{"leave_type": "PAID", "remaining_days": 10}],
        team_availability=[
            {"date": "2026-03-10", "availability_rate": 0.9},
            {"date": "2026-03-11", "availability_rate": 0.85},
            {"date": "2026-03-12", "availability_rate": 0.88},
        ],
    )
    result = engine.recommend_leave(request)
    assert result.conflict_level == ConflictLevel.LOW
    assert result.recommendation
    assert result.reasons
    assert result.supporting_factors


def test_high_conflict_insufficient_balance_and_staffing():
    engine = AIEngine()
    request = LeaveRecommendationRequest(
        employee_id="EMP002",
        start_date="2026-03-10",
        end_date="2026-03-14",
        leave_type="PAID",
        leave_balances=[{"leave_type": "PAID", "remaining_days": 1}],
        existing_leave=[{"start_date": "2026-03-11", "end_date": "2026-03-13"}],
        team_availability=[
            {"date": "2026-03-10", "availability_rate": 0.5},
            {"date": "2026-03-11", "availability_rate": 0.45},
        ],
        department_staffing={"total_employees": 6},
    )
    result = engine.recommend_leave(request)
    assert result.conflict_level == ConflictLevel.HIGH
    assert any("balance" in r.lower() or "availability" in r.lower() for r in result.reasons)
