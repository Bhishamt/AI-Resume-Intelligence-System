"""
Persona selection engine.

Loads role-specific persona templates from data/personas/ and selects
the best match based on keyword frequency analysis against the target
job description.
"""

import os
import re

from src.utils.config import Config
from src.utils.helpers import load_json_file


class PersonaSelector:
    """Matches a job description to the most relevant resume persona."""

    PERSONAS_DIR = os.path.join(Config.DATA_DIR, "personas")

    @classmethod
    def load_all_personas(cls) -> list[dict]:
        """Loads every .json file in the personas directory."""
        personas: list[dict] = []
        if not os.path.isdir(cls.PERSONAS_DIR):
            return personas
        for fname in sorted(os.listdir(cls.PERSONAS_DIR)):
            if fname.endswith(".json"):
                path = os.path.join(cls.PERSONAS_DIR, fname)
                data = load_json_file(path)
                if data:
                    data["_filename"] = fname
                    personas.append(data)
        return personas

    @classmethod
    def select_best_persona(cls, job_description: str) -> dict | None:
        """
        Scores each persona against the job description by counting
        how many of its ``match_keywords`` appear, then returns the
        highest-scoring persona (or *None* if no personas are found).
        """
        personas = cls.load_all_personas()
        if not personas:
            return None

        jd_lower = job_description.lower()
        best_score  = -1
        best_persona = None

        for persona in personas:
            score = 0
            for keyword in persona.get("match_keywords", []):
                pattern = rf"\b{re.escape(keyword.lower())}\b"
                score += len(re.findall(pattern, jd_lower))

            if score > best_score:
                best_score  = score
                best_persona = persona

        if best_persona is not None:
            best_persona["_match_score"] = best_score

        return best_persona
