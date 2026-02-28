"""
Gemini LLM Service — uses the **google.genai** SDK exclusively.

The deprecated ``google.generativeai`` package has been removed.
"""

import logging
from typing import Sequence

from app.core.config import settings
from app.models.chat_message import ChatMessage

logger = logging.getLogger(__name__)

try:
    from google import genai
    from google.genai import types as genai_types
except ImportError:
    genai = None  # type: ignore[assignment]
    genai_types = None  # type: ignore[assignment]


class GeminiService:
    """Wrapper around Google Gemini via the ``google.genai`` SDK."""

    def __init__(self) -> None:
        self._client = None
        if not settings.google_api_key:
            logger.warning("GOOGLE_API_KEY not set — Gemini disabled.")
            return
        if genai is None:
            logger.warning("google-genai package not installed — Gemini disabled.")
            return
        try:
            self._client = genai.Client(api_key=settings.google_api_key)
            logger.info("Gemini client initialised (model=%s).", settings.gemini_model)
        except Exception:
            logger.exception("Failed to create Gemini client.")
            self._client = None

    @property
    def enabled(self) -> bool:
        return self._client is not None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_prompt(self, history: Sequence[ChatMessage], user_text: str) -> str:
        lines: list[str] = ["Conversation context:"]
        for msg in history:
            role = msg.role.value.upper()
            content = (msg.content or "").strip()
            if content:
                lines.append(f"[{role}] {content}")
        lines.append(f"[USER] {user_text}")
        lines.append("[ASSISTANT]")
        return "\n".join(lines)

    def _generate(self, prompt: str, system_instruction: str | None = None) -> str | None:
        """Low-level call to Gemini. Returns text or *None* on failure."""
        if not self.enabled:
            return None
        try:
            config: dict = {}
            if system_instruction:
                config["system_instruction"] = system_instruction
            result = self._client.models.generate_content(  # type: ignore[union-attr]
                model=settings.gemini_model,
                contents=prompt,
                config=config,
            )
            text = getattr(result, "text", "") or ""
            return text.strip() or None
        except Exception:
            logger.exception("Gemini generate_content failed.")
            return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_response(self, history: Sequence[ChatMessage], user_text: str) -> str:
        if not self.enabled:
            return (
                "Gemini is not configured. Please set GOOGLE_API_KEY to enable AI responses. "
                "Your message has been stored successfully."
            )

        prompt = self._build_prompt(history, user_text)
        text = self._generate(prompt, settings.system_prompt)
        if text:
            return text

        return (
            "Gemini is configured but the request failed (model/key may be invalid). "
            "Your message has been stored successfully."
        )

    def summarize_text(self, text: str, max_words: int = 180) -> str:
        prompt = (
            "Summarize the following academic document in Vietnamese with an academic style. "
            f"Limit to around {max_words} words and include core contributions, methods, and limitations.\n\n"
            f"{text}"
        )
        if not self.enabled:
            clipped = " ".join(text.split()[:max_words])
            return f"Tóm tắt (fallback khi Gemini chưa cấu hình): {clipped}"

        result = self._generate(prompt, settings.system_prompt)
        if result:
            return result

        clipped = " ".join(text.split()[:max_words])
        return f"Tóm tắt (fallback do Gemini lỗi): {clipped}"


gemini_service = GeminiService()
