"""Attendance anomaly detection tests."""

from services.engine import AIEngine

from helpers import make_anomalous_records, make_normal_records


def test_normal_attendance_no_anomaly():
    engine = AIEngine()
    records = make_normal_records()
    results = engine.detect_anomalies(records)
    assert results == []


def test_anomalous_attendance_detected():
    engine = AIEngine()
    records = make_anomalous_records()
    results = engine.detect_anomalies(records)
    assert len(results) >= 1
    item = results[0]
    assert item.employee_id == "EMP002"
    assert item.anomaly is True
    assert item.severity in {"LOW", "MEDIUM", "HIGH"}
    assert item.reason
    assert item.supporting_factors
    assert item.recommendation


def test_missing_data_skips_short_history():
    engine = AIEngine()
    records = make_normal_records(days=3)
    assert engine.detect_anomalies(records) == []


def test_missing_employee_id_ignored():
    engine = AIEngine()
    records = [{"check_in_time": "09:00", "working_hours": 8}]
    assert engine.detect_anomalies(records) == []
