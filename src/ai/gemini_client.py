"""
Gemini API client using the modern google-genai SDK.

Features
────────
  - Configurable model (via GEMINI_MODEL env var)
  - Native JSON response mode (response_mime_type)
  - Proper system_instruction parameter (not prompt-concatenation)
  - Automatic retries with exponential backoff
  - Health-check endpoint for provider status UI
"""

from src.utils.config import Config

# Graceful import — allows the rest of the app to function if the
# user hasn't installed google-genai yet.
try:
    from google import genai
    from google.genai import types

    _GENAI_AVAILABLE = True
except ImportError:
    _GENAI_AVAILABLE = False

from tenacity import retry, stop_after_attempt, wait_exponential


class GeminiClient:
    """Google Gemini API client with retry logic and structured JSON mode."""

    DEFAULT_MODEL = "gemini-2.0-flash"

    def __init__(self) -> None:
        self.api_key    = Config.GEMINI_API_KEY
        self.model_name = getattr(Config, "GEMINI_MODEL", None) or self.DEFAULT_MODEL
        self.client     = None
        self._healthy   = False

        if _GENAI_AVAILABLE and self.api_key:
            try:
                self.client  = genai.Client(api_key=self.api_key)
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
        """
        Sends a prompt to Gemini and returns the response text.

        Parameters
        ----------
        prompt : str
            The user-facing prompt.
        system_instruction : str
            Passed via the SDK's native ``system_instruction`` config
            (not concatenated into the prompt).
        json_mode : bool
            When True, instructs the model to return valid JSON via
            ``response_mime_type``.
        """
        if not self.client:
            raise ConnectionError(
                "Gemini client not initialised. "
                "Ensure google-genai is installed and GEMINI_API_KEY is set."
            )

        cfg: dict = {
            "temperature":      0.7,
            "max_output_tokens": 4096,
        }
        if system_instruction:
            cfg["system_instruction"] = system_instruction
        if json_mode:
            cfg["response_mime_type"] = "application/json"

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(**cfg),
            )
            self._healthy = True
            return response.text
        except Exception:
            self._healthy = False
            raise

    # ── Health check ─────────────────────────────────────────────────

    def health_check(self) -> dict:
        if not _GENAI_AVAILABLE:
            return {"status": "unavailable", "reason": "google-genai not installed"}
        if not self.client:
            return {"status": "unavailable", "reason": "API key not set"}
        try:
            self.client.models.generate_content(
                model=self.model_name,
                contents="Reply with the single word OK",
                config=types.GenerateContentConfig(max_output_tokens=10),
            )
            self._healthy = True
            return {"status": "healthy"}
        except Exception as exc:
            self._healthy = False
            return {"status": "error", "reason": str(exc)[:120]}
