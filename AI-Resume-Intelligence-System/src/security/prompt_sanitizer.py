"""
Prompt sanitisation and injection prevention.

Protects the AI pipeline against:
  - Prompt injection attacks (e.g. "ignore previous instructions")
  - Hidden system-level instructions embedded in job descriptions
  - Malicious unicode / invisible control characters
  - Excessively long inputs designed to overwhelm context windows
"""

import re
import unicodedata


class PromptSanitizer:
    """Cleans and validates user-supplied text before it enters the AI pipeline."""

    MAX_INPUT_LENGTH = 15_000  # characters

    # Regex patterns that signal prompt-injection attempts
    INJECTION_PATTERNS: list[str] = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"forget\s+(all\s+)?(your\s+)?previous",
        r"disregard\s+(all\s+)?prior",
        r"you\s+are\s+now\s+a",
        r"act\s+as\s+if\s+you",
        r"pretend\s+you\s+are",
        r"new\s+instructions?\s*:",
        r"system\s*:\s*",
        r"<\s*/?script",
        r"javascript\s*:",
        r"\[\s*INST\s*\]",
        r"\[\s*/?\s*SYS(?:TEM)?\s*\]",
        r"<<\s*SYS\s*>>",
        r"BEGIN\s+OVERRIDE",
        r"ADMIN\s+MODE",
        r"DEBUG\s+MODE",
        r"DEVELOPER\s+MODE",
        r"IGNORE\s+SAFETY",
        r"JAILBREAK",
        r"DAN\s+MODE",
    ]

    _compiled = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]

    # ── Public API ───────────────────────────────────────────────────

    @classmethod
    def sanitize(cls, text: str) -> tuple[str, list[str]]:
        """
        Sanitises user input text.

        Returns
        -------
        (sanitised_text, list_of_warnings)
            The cleaned text and a list of human-readable warning strings.
        """
        warnings: list[str] = []

        if not text:
            return "", []

        # 1 — Length limit
        if len(text) > cls.MAX_INPUT_LENGTH:
            text = text[: cls.MAX_INPUT_LENGTH]
            warnings.append(
                f"Input truncated to {cls.MAX_INPUT_LENGTH:,} characters."
            )

        # 2 — Strip invisible / control characters (preserve \n \r \t)
        cleaned: list[str] = []
        for ch in text:
            cat = unicodedata.category(ch)
            if cat.startswith("C") and ch not in ("\n", "\r", "\t"):
                continue
            if cat == "Cf":  # zero-width joiners, BOM, etc.
                continue
            cleaned.append(ch)
        text = "".join(cleaned)

        # 3 — Detect injection patterns
        for pattern in cls._compiled:
            match = pattern.search(text)
            if match:
                warnings.append(
                    f"Potential prompt injection detected: \"{match.group()}\""
                )

        # 4 — Normalise excessive whitespace
        text = re.sub(r"\n{4,}", "\n\n\n", text)
        text = re.sub(r"[ \t]{4,}", "   ", text)

        return text.strip(), warnings

    @classmethod
    def is_safe(cls, text: str) -> bool:
        """Returns True if no injection patterns are detected."""
        _, warnings = cls.sanitize(text)
        return len(warnings) == 0
