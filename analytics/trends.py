"""Time-series trend aggregations."""

from __future__ import annotations

from collections import defaultdict
from datetime import date


def _parse_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def get_attendance_trend(records: list[dict], period: str = "monthly") -> list[dict]:
    """Aggregate attendance records into monthly time-series trend."""
    buckets: dict[str, list[str]] = defaultdict(list)
    for r in records:
        d = _parse_date(r["date"])
        key = d.strftime("%Y-%m") if period == "monthly" else d.strftime("%Y-W%W")
        buckets[key].append(r.get("status", "ABSENT"))

    trend = []
    for month in sorted(buckets.keys()):
        statuses = buckets[month]
        present = sum(1 for s in statuses if s == "PRESENT")
        rate = round(present / len(statuses), 2) if statuses else 0.0
        trend.append({"month": month, "rate": rate})
    return trend[-6:]


def get_leave_trend(records: list[dict], period: str = "monthly") -> list[dict]:
    """Aggregate leave records into monthly time-series trend."""
    buckets: dict[str, int] = defaultdict(int)
    for lr in records:
        if lr.get("status") not in {"APPROVED", "PENDING"}:
            continue
        start = _parse_date(lr["start_date"])
        key = start.strftime("%Y-%m") if period == "monthly" else start.strftime("%Y-W%W")
        end = _parse_date(lr["end_date"])
        buckets[key] += (end - start).days + 1

    trend = [{"month": month, "count": count} for month, count in sorted(buckets.items())]
    return trend[-6:]
