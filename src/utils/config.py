import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

class AppConfig(BaseSettings):
    """Centralised configuration with automatic dev/prod profile switching."""

    # Core paths
    PROJECT_ROOT: str = _PROJECT_ROOT
    DATA_DIR: str = os.path.join(_PROJECT_ROOT, "data")
    OUTPUT_DIR: str = os.path.join(_PROJECT_ROOT, "exports")
    TEMPLATE_DIR: str = os.path.join(_PROJECT_ROOT, "data", "templates")

    # API keys
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    # Model configuration
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # Application mode
    APP_MODE: str = "dev"
    
    # Profile mapping override via env
    PROFILE_FILENAME: str | None = None

    model_config = SettingsConfigDict(
        env_file=os.path.join(_PROJECT_ROOT, ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def MASTER_RESUME_PATH(self) -> str:
        if self.PROFILE_FILENAME:
            filename = self.PROFILE_FILENAME
        else:
            filename = "profile.local.json" if self.APP_MODE.lower().strip() == "dev" else "profile.production.json"
        return os.path.join(self.DATA_DIR, filename)

    @property
    def ATS_KEYWORDS_PATH(self) -> str:
        return os.path.join(self.DATA_DIR, "ats_keywords.json")

    def validate_config(self) -> List[str]:
        """Returns a list of warning strings for any mis-configured values."""
        warnings: List[str] = []

        if not self.GEMINI_API_KEY:
            warnings.append(
                "GEMINI_API_KEY is not set. AI functions will use fallback provider or mock responses."
            )

        if not self.GROQ_API_KEY:
            warnings.append(
                "GROQ_API_KEY is not set. Groq fallback will be unavailable."
            )

        if not os.path.isfile(self.MASTER_RESUME_PATH):
            warnings.append(
                f"Profile file not found: {self.MASTER_RESUME_PATH}. "
                "Copy master_resume.template.json and populate your data."
            )

        if not os.path.isfile(self.ATS_KEYWORDS_PATH):
            warnings.append(
                f"ATS keywords file not found: {self.ATS_KEYWORDS_PATH}."
            )

        return warnings

Config = AppConfig()
