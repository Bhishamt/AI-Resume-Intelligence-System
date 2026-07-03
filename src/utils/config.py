import os
from dotenv import load_dotenv

# ── Resolve project root (two levels up from src/utils/config.py) ──
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Load .env from project root
load_dotenv(os.path.join(_PROJECT_ROOT, ".env"))


class Config:
    """Centralised configuration with automatic dev/prod profile switching."""

    # ── Core paths ───────────────────────────────────────────────────
    PROJECT_ROOT = _PROJECT_ROOT
    DATA_DIR     = os.path.join(PROJECT_ROOT, "data")
    OUTPUT_DIR   = os.path.join(PROJECT_ROOT, "exports")
    TEMPLATE_DIR = os.path.join(DATA_DIR, "templates")

    # ── API keys ─────────────────────────────────────────────────────
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")

    # ── Model configuration ──────────────────────────────────────────
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    # ── Application mode ─────────────────────────────────────────────
    APP_MODE = os.getenv("APP_MODE", "dev").lower().strip()

    # ── Profile switching ────────────────────────────────────────────
    _PROFILE_MAP = {
        "dev":  "profile.local.json",
        "prod": "profile.production.json",
    }
    MASTER_RESUME_PATH = os.path.join(
        DATA_DIR,
        _PROFILE_MAP.get(APP_MODE, "profile.local.json"),
    )

    # ── Static data ──────────────────────────────────────────────────
    ATS_KEYWORDS_PATH = os.path.join(DATA_DIR, "ats_keywords.json")

    # ── Validation ───────────────────────────────────────────────────
    @classmethod
    def validate(cls) -> list[str]:
        """Returns a list of warning strings for any mis-configured values."""
        warnings: list[str] = []

        if not cls.GEMINI_API_KEY:
            warnings.append(
                "GEMINI_API_KEY is not set. AI functions will use fallback provider or mock responses."
            )

        if not cls.GROQ_API_KEY:
            warnings.append(
                "GROQ_API_KEY is not set. Groq fallback will be unavailable."
            )

        if not os.path.isfile(cls.MASTER_RESUME_PATH):
            warnings.append(
                f"Profile file not found: {cls.MASTER_RESUME_PATH}. "
                "Copy master_resume.template.json and populate your data."
            )

        if not os.path.isfile(cls.ATS_KEYWORDS_PATH):
            warnings.append(
                f"ATS keywords file not found: {cls.ATS_KEYWORDS_PATH}."
            )

        return warnings
