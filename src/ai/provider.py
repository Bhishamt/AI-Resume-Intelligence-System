"""
Unified AI provider with automatic failover.

    Gemini (primary)  →  Groq (fallback)  →  error message

Tracks real-time health status of each provider for the sidebar UI.
"""

from src.ai.gemini_client import GeminiClient
from src.ai.groq_client import GroqClient


class AIProvider:
    """Single entry-point for all AI text generation in the application."""

    def __init__(self) -> None:
        self.gemini = GeminiClient()
        self.groq   = GroqClient()

        self.active_provider: str = "none"
        self.status: dict[str, str] = {
            "gemini": "ready" if self.gemini.is_available else "unavailable",
            "groq":   "ready" if self.groq.is_available   else "unavailable",
        }

    # ── Generation with failover ─────────────────────────────────────

    def generate_text(
        self,
        prompt: str,
        system_instruction: str = "",
        json_mode: bool = False,
    ) -> str:
        """
        Tries Gemini first; on any failure, falls back to Groq.
        Returns an error string only if both providers fail.
        """
        # ── Primary: Gemini ──────────────────────────────────────────
        if self.gemini.is_available:
            try:
                result = self.gemini.generate_text(
                    prompt, system_instruction, json_mode
                )
                self.active_provider  = "gemini"
                self.status["gemini"] = "healthy"
                return result
            except Exception as exc:
                self.status["gemini"] = f"error: {type(exc).__name__}"

        # ── Fallback: Groq ───────────────────────────────────────────
        if self.groq.is_available:
            try:
                result = self.groq.generate_text(
                    prompt, system_instruction, json_mode
                )
                self.active_provider = "groq"
                self.status["groq"]  = "healthy"
                return result
            except Exception as exc:
                self.status["groq"] = f"error: {type(exc).__name__}"

        # ── All providers down ───────────────────────────────────────
        self.active_provider = "none"
        return (
            "[AI Error] All providers failed. "
            "Check your API keys and network connection."
        )

    # ── Health checks ────────────────────────────────────────────────

    def run_health_checks(self) -> dict[str, dict]:
        """Pings each provider and updates ``self.status``."""
        results: dict[str, dict] = {}

        results["gemini"] = self.gemini.health_check()
        results["groq"]   = self.groq.health_check()

        for name, result in results.items():
            self.status[name] = result.get("status", "unknown")

        return results
