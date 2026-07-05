"""
Export versioning and history tracking (SQLite backed).

Stores metadata for every resume / cover-letter export so users can
track which version was sent to which company, along with the ATS score
at the time of generation.

Directory layout
────────────────
exports/
  history/
    exports.db             ← SQLite database
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
from src.utils.database import get_connection


class ExportHistory:
    """Manages a local export history using SQLite."""

    HISTORY_DIR = os.path.join(Config.OUTPUT_DIR, "history")

    @classmethod
    def _ensure_dirs(cls) -> None:
        os.makedirs(cls.HISTORY_DIR, exist_ok=True)

    @classmethod
    def get_next_version_number(cls) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM generations")
        count = cursor.fetchone()[0]
        conn.close()
        return count + 1

    @classmethod
    def save_generation(
        cls,
        company: str,
        job_title: str,
        raw_text: str,
        persona: str,
        ats_score: float,
        recruiter_score: float,
        keyword_match_pct: float,
        missing_skills: list[str],
        recommended_skills: list[str],
        ranked_projects: list[dict],
        exported_files: list[str],
    ) -> dict:
        """
        Archives the current exports into a numbered version directory
        and appends metadata to the SQLite database.
        """
        cls._ensure_dirs()
        version = cls.get_next_version_number()
        
        version_dir = os.path.join(cls.HISTORY_DIR, f"v{version:04d}")
        os.makedirs(version_dir, exist_ok=True)

        copied: list[str] = []
        for fpath in exported_files:
            if os.path.isfile(fpath):
                dest = os.path.join(version_dir, os.path.basename(fpath))
                shutil.copy2(fpath, dest)
                copied.append(os.path.basename(fpath))
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Insert job analysis
        cursor.execute('''
            INSERT INTO job_analysis (job_title, company, raw_text)
            VALUES (?, ?, ?)
        ''', (job_title, company, raw_text))
        job_id = cursor.lastrowid
        
        # Insert generation
        cursor.execute('''
            INSERT INTO generations (
                job_id, persona, ats_score, recruiter_score, 
                keyword_match_pct, missing_skills, recommended_skills, files_exported
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            job_id, persona, ats_score, recruiter_score, keyword_match_pct,
            json.dumps(missing_skills), json.dumps(recommended_skills), json.dumps(copied)
        ))
        generation_id = cursor.lastrowid
        
        # Insert project rankings
        for proj in ranked_projects:
            cursor.execute('''
                INSERT INTO project_rankings (generation_id, project_title, relevance_score)
                VALUES (?, ?, ?)
            ''', (generation_id, proj.get("title", ""), proj.get("relevance_score", 0.0)))
            
        conn.commit()
        conn.close()

        # Update manifest.json
        manifest_path = os.path.join(cls.HISTORY_DIR, "manifest.json")
        manifest_data = []
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest_data = json.load(f)
            except Exception:
                pass
                
        manifest_data.append({
            "Version": f"v{version:04d}",
            "Date": datetime.now().isoformat(),
            "Company": company,
            "Job Title": job_title,
            "ATS Score": ats_score,
            "Recruiter Score": recruiter_score,
            "Selected Persona": persona,
            "Selected Projects": [p.get("title", "") for p in ranked_projects]
        })
        
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=4)

        return {
            "version": version,
            "company": company,
            "job_title": job_title,
            "ats_score": ats_score,
            "files": copied
        }
