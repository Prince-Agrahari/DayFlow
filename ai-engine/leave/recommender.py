"""Smart leave recommendation — HR decision support only."""

from __future__ import annotations

from datetime import date, timedelta

from schemas.models import ConflictLevel, LeaveRecommendationRequest, LeaveRecommendationResult


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _date_range(start: date, end: date) -> list[date]:
    days = []
    current = start
    while current <= end:
        days.append(current)
        current += timedelta(days=1)
    return days


def recommend_leave(request: LeaveRecommendationRequest) -> LeaveRecommendationResult:
    """Analyze leave conflict — HR makes the final decision."""
    start = _parse_date(request.start_date)
    end = _parse_date(request.end_date)
    requested_days = (end - start).days + 1

    factors: list[str] = []
    reasons: list[str] = []
    conflict_score = 0.0

    paid_balance = next((b for b in request.leave_balances if b.get("leave_type") == "PAID"), None)
    if paid_balance:
        remaining = float(paid_balance.get("remaining_days", paid_balance.get("total_days", 0) - paid_balance.get("used_days", 0)))
        factors.append(f"Paid leave balance: {remaining} days remaining")
        if request.leave_type == "PAID" and remaining < requested_days:
            conflict_score += 0.4
            reasons.append(f"Insufficient paid leave balance ({remaining} days remaining, {requested_days} requested)")

    overlapping = 0
    for leave in request.existing_leave:
        ls = _parse_date(leave["start_date"])
        le = _parse_date(leave["end_date"])
        if not (end < ls or start > le):
            overlapping += 1
    if overlapping:
        conflict_score += min(overlapping * 0.15, 0.45)
        factors.append(f"Overlapping approved leave requests: {overlapping}")
        reasons.append(f"{overlapping} team member(s) already on leave during requested dates")

    dept = request.department_staffing
    total_staff = int(dept.get("total_employees", 8) or 8)
    request_dates = _date_range(start, end)

    min_availability = 1.0
    for d in request_dates:
        ds = d.isoformat()
        day_avail = next((a for a in request.team_availability if a.get("date") == ds), None)
        if day_avail:
            rate = float(day_avail.get("availability_rate", 1.0))
            min_availability = min(min_availability, rate)
            factors.append(f"Team availability on {ds}: {rate:.0%}")

    if min_availability < 0.6:
        conflict_score += 0.35
        reasons.append(f"Team availability drops to {min_availability:.0%} during requested period")
    elif min_availability < 0.75:
        conflict_score += 0.15
        reasons.append(f"Team availability at {min_availability:.0%} — moderate staffing impact")

    if not reasons:
        reasons.append("No significant scheduling conflicts detected")
        factors.append(f"Requested duration: {requested_days} day(s)")

    if conflict_score >= 0.5:
        level = ConflictLevel.HIGH
        recommendation = "Review team coverage plan before approving; consider alternative dates or partial approval"
    elif conflict_score >= 0.25:
        level = ConflictLevel.MEDIUM
        recommendation = "Consider approving with a documented team coverage plan"
    else:
        level = ConflictLevel.LOW
        recommendation = "Low conflict detected — approval appears reasonable pending HR review"

    return LeaveRecommendationResult(
        conflict_level=level,
        recommendation=recommendation,
        reasons=reasons,
        supporting_factors=factors,
    )
