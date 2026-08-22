"""Isolation Forest attendance anomaly detection."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime

import numpy as np
from sklearn.ensemble import IsolationForest

from schemas.models import AnomalyResult, AnomalySeverity

MIN_RECORDS = 5
WORK_START_HOUR = 9.0


def _parse_hour(value: str | None, default: float = WORK_START_HOUR) -> float:
    if not value:
        return default
    try:
        if "T" in value:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).hour + datetime.fromisoformat(value.replace("Z", "+00:00")).minute / 60
        return float(value)
    except (ValueError, TypeError):
        return default


def _extract_features(records: list[dict]) -> np.ndarray:
    features = []
    for r in records:
        status = str(r.get("status", "PRESENT")).upper()
        is_absent = 1.0 if status == "ABSENT" else 0.0
        is_late = 1.0 if r.get("is_late") else 0.0
        hours = float(r.get("working_hours") or (0.0 if is_absent else 8.0))
        check_in = _parse_hour(r.get("check_in_time"))
        check_out = _parse_hour(r.get("check_out_time"), default=check_in + hours)
        features.append([check_in, check_out, hours, is_late, is_absent])
    return np.array(features)


def _severity_from_score(score: float) -> AnomalySeverity:
    if score <= -0.5:
        return AnomalySeverity.HIGH
    if score <= -0.25:
        return AnomalySeverity.MEDIUM
    return AnomalySeverity.LOW


def _build_reason(records: list[dict], factors: list[str]) -> str:
    late_rate = sum(1 for r in records if r.get("is_late")) / max(len(records), 1)
    absent_rate = sum(1 for r in records if str(r.get("status", "")).upper() == "ABSENT") / max(len(records), 1)
    parts = []
    if late_rate > 0.3:
        parts.append(f"Late arrival rate {late_rate:.0%} exceeds baseline")
    if absent_rate > 0.15:
        parts.append(f"Absence frequency {absent_rate:.0%} is elevated")
    if factors:
        parts.extend(factors[:2])
    return "; ".join(parts) if parts else "Attendance pattern deviates from historical baseline"


def detect_anomalies(attendance_records: list[dict]) -> list[AnomalyResult]:
    """Detect attendance anomalies using Isolation Forest per employee."""
    grouped: dict[str, list[dict]] = defaultdict(list)
    for record in attendance_records:
        eid = record.get("employee_id")
        if eid:
            grouped[eid].append(record)

    results: list[AnomalyResult] = []
    for employee_id, records in grouped.items():
        if len(records) < MIN_RECORDS:
            continue

        features = _extract_features(records)
        model = IsolationForest(contamination=0.15, random_state=42, n_estimators=100)
        model.fit(features)
        scores = model.decision_function(features)
        predictions = model.predict(features)

        avg_score = float(np.mean(scores))
        anomaly_flags = predictions == -1
        is_anomaly = bool(np.any(anomaly_flags))

        if not is_anomaly and avg_score > -0.1:
            continue

        late_count = sum(1 for r in records if r.get("is_late"))
        absent_count = sum(1 for r in records if str(r.get("status", "")).upper() == "ABSENT")
        avg_hours = float(np.mean([float(r.get("working_hours") or 8) for r in records]))
        factors = [
            f"Late arrivals: {late_count}/{len(records)} days",
            f"Absences: {absent_count}/{len(records)} days",
            f"Average working hours: {avg_hours:.1f}",
        ]

        severity = _severity_from_score(avg_score)
        reason = _build_reason(records, factors)
        recommendation = (
            "Review attendance history with the employee and monitor pattern over the next 2 weeks."
            if severity == AnomalySeverity.HIGH
            else "Monitor attendance pattern and consider a supportive check-in if trend continues."
        )

        results.append(
            AnomalyResult(
                employee_id=employee_id,
                employee_name=records[0].get("employee_name"),
                anomaly=True,
                score=round(avg_score, 3),
                severity=severity,
                reason=reason,
                supporting_factors=factors,
                recommendation=recommendation,
            )
        )

    results.sort(key=lambda x: x.score)
    return results
