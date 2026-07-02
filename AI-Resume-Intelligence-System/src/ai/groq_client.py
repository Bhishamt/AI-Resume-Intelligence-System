"""
Groq API client — fast LLM fallback provider.

Features
────────
  - Real Groq SDK integration (groq package)
  - JSON response mode via response_format
  - Proper system / user message separation
  - Automatic retries with exponential backoff
  - Health-check endpoint for provider status UI
"""

from src.utils.config import Config

try:
    from groq import Groq

    _GROQ_AVAILABLE = True
except ImportError:
    _GROQ_AVAILABLE = False

from tenacity import retry, stop_after_attempt, wait_exponential


class GroqClient:
    """Groq API client backed by the groq Python SDK."""

    DEFAULT_MODEL = "llama-3.3-70b-versatile"

    def __init__(self) -> None:
        self.api_key    = Config.GROQ_API_KEY
        self.model_name = self.DEFAULT_MODEL
        self.client     = None
        self._healthy   = False

        if _GROQ_AVAILABLE and self.api_key:
            try:
                self.client  = Groq(api_key=self.api_key)
                self._healthy = True
            except Exception:
                self.client = None

    # ── Status ───────────────────────────────────────────────────────

    @property
    def is_available(self) -> bool:
        return self.client is not None and self._healthy

    # ── Generation ───────────────────────────────────────────────────

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def generate_text(
        self,
        prompt: str,
        system_instruction: str = "",
        json_mode: bool = False,
    ) -> str:
        """Sends a prompt to Groq and returns the response text."""
        if not self.client:
            raise ConnectionError(
                "Groq client not initialised. "
                "Ensure groq is installed and GROQ_API_KEY is set."
            )

        messages: list[dict] = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        kwargs: dict = {
            "model":       self.model_name,
            "messages":    messages,
            "temperature": 0.7,
            "max_tokens":  4096,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            resp = self.client.chat.completions.create(**kwargs)
            self._healthy = True
            return resp.choices[0].message.content
        except Exception:
            self._healthy = False
            raise

    # ── Health check ─────────────────────────────────────────────────

    def health_check(self) -> dict:
        if not _GROQ_AVAILABLE:
            return {"status": "unavailable", "reason": "groq package not installed"}
        if not self.client:
            return {"status": "unavailable", "reason": "API key not set"}
        try:
            self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": "Reply OK"}],
                max_tokens=10,
            )
            self._healthy = True
            return {"status": "healthy"}
        except Exception as exc:
            self._healthy = False
            return {"status": "error", "reason": str(exc)[:120]}
