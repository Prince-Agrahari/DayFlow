"""Shared Gemini client — server-side only."""

from __future__ import annotations

import json
import os
from typing import Any


class GeminiError(Exception):
    """Raised when Gemini API call fails."""


def call_gemini(*, api_key: str, model: str, system_prompt: str, user_prompt: str) -> str:
    if not api_key:
        raise GeminiError("GEMINI_API_KEY is not configured")

    try:
        import google.generativeai as genai
    except ImportError as exc:
        raise GeminiError("google-generativeai package is not installed") from exc

    genai.configure(api_key=api_key)
    gemini_model = genai.GenerativeModel(model_name=model, system_instruction=system_prompt)
    response = gemini_model.generate_content(user_prompt)
    text = getattr(response, "text", None)
    if not text:
        raise GeminiError("Empty response from Gemini API")
    return text.strip()


def structured_context_block(context: dict[str, Any]) -> str:
    return json.dumps(context, indent=2, default=str)
