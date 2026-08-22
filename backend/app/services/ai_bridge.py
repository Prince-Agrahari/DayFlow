"""Bridge to ai-engine package (adds ai-engine/ to Python path)."""

from __future__ import annotations

import sys
from pathlib import Path

from app.config import settings

_AI_ROOT = Path(__file__).resolve().parents[3] / "ai-engine"


def _ensure_ai_engine_path() -> None:
    ai_path = str(_AI_ROOT)
    if ai_path not in sys.path:
        sys.path.insert(0, ai_path)


def get_engine():
    _ensure_ai_engine_path()
    from services.engine import AIEngine

    return AIEngine(gemini_api_key=settings.gemini_api_key, gemini_model=settings.gemini_model)


def build_leave_request(data: dict):
    _ensure_ai_engine_path()
    from schemas.models import LeaveRecommendationRequest

    return LeaveRecommendationRequest(**data)
