"""Smoke test — AI engine facade starts."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.engine import AIEngine


def test_engine_starts():
    engine = AIEngine(gemini_api_key="", gemini_model="gemini-2.0-flash")
    assert engine.gemini_model == "gemini-2.0-flash"
    assert engine.detect_anomalies([]) == []
