"""
Export versioning and history tracking.

Stores metadata for every resume / cover-letter export so users can
track which version was sent to which company, along with the ATS score
at the time of generation.

Directory layout
────────────────
exports/
  history/
    manifest.json          ← append-only version log
    v0001/
      optimized_resume.pdf
      optimized_resume.docx
    v0002/
      ...
"""

import json
import os
import shutil
from datetime import datetime

from src.utils.config import Config


class ExportHistory:
    """Manages a local, append-only export history."""

    HISTORY_DIR   = os.path.join(Config.OUTPUT_DIR, "history")
    MANIFEST_FILE = os.path.join(HISTORY_DIR, "manifest.json")

    # ── Internal helpers ─────────────────────────────────────────────

    @classmethod
    def _ensure_dirs(cls) -> None:
        os.makedirs(cls.HISTORY_DIR, exist_ok=True)

    @classmethod
    def _load_manifest(cls) -> list[dict]:
        if os.path.isfile(cls.MANIFEST_FILE):
            try:
                with open(cls.MANIFEST_FILE, "r", encoding="utf-8") as fh:
                    return json.load(fh)
            except (json.JSONDecodeError, OSError):
                return []
        return []

    @classmethod
    def _save_manifest(cls, entries: list[dict]) -> None:
        with open(cls.MANIFEST_FILE, "w", encoding="utf-8") as fh:
            json.dump(entries, fh, indent=2, ensure_ascii=False)

    # ── Public API ───────────────────────────────────────────────────

    @classmethod
    def save_version(
        cls,
        company: str,
        job_title: str,
        ats_score: float,
        exported_files: list[str],
    ) -> dict:
        """
        Archives the current exports into a numbered version directory
        and appends metadata to the manifest.

        Returns the newly created version entry dict.
        """
        cls._ensure_dirs()

        manifest = cls._load_manifest()
        version  = len(manifest) + 1
        ts       = datetime.now().isoformat()

        version_dir = os.path.join(cls.HISTORY_DIR, f"v{version:04d}")
        os.makedirs(version_dir, exist_ok=True)

        copied: list[str] = []
        for fpath in exported_files:
            if os.path.isfile(fpath):
                dest = os.path.join(version_dir, os.path.basename(fpath))
                shutil.copy2(fpath, dest)
                copied.append(os.path.basename(fpath))

        entry = {
            "version":   version,
            "company":   company,
            "job_title":  job_title,
            "ats_score":  ats_score,
            "date":       ts,
            "files":      copied,
        }

        manifest.append(entry)
        cls._save_manifest(manifest)
        return entry

    @classmethod
    def list_versions(cls) -> list[dict]:
        """Returns the full manifest (oldest → newest)."""
        return cls._load_manifest()
