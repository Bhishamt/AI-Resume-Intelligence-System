"""
Resume generator with a complete optimisation pipeline:

  AIProvider (Gemini → Groq fallback)
        ↓
  Structured JSON prompt (with persona context)
        ↓
  JSON Parser → Pydantic Validation (OptimizedOutput)
        ↓
  Merge: Summary → Experience → Projects → Skills
        ↓
  Export-ready dict for PDF / DOCX
"""

import copy
import json
import re

from src.ai.prompt_engine import PromptEngine
from src.models.resume_models import OptimizedOutput
from src.utils.config import Config
from src.utils.helpers import load_json_file


class ResumeGenerator:
    def __init__(self, ai_provider=None):
        if ai_provider is None:
            from src.ai.provider import AIProvider
            ai_provider = AIProvider()
        self.ai = ai_provider

    # ── Public API ───────────────────────────────────────────────────

    def generate_optimized_resume(
        self,
        job_desc: str,
        extracted_keywords: list,
        persona: dict | None = None,
    ) -> dict:
        """
        Full pipeline:
          1. Load the master resume from the active profile.
          2. Build a structured-JSON prompt (with optional persona).
          3. Call AIProvider (Gemini → Groq failover).
          4. Parse response → Pydantic validation.
          5. Merge optimised fields back into the resume dict.
          6. Return the export-ready dict.
        """
        master = load_json_file(Config.MASTER_RESUME_PATH)
        if not master:
            return {}

        optimized = copy.deepcopy(master)

        prompt = PromptEngine.build_resume_optimization_prompt(
            master_profile=master,
            job_description=job_desc,
            target_keywords=extracted_keywords,
            persona=persona,
        )

        system_instruction = (
            "Optimise the resume using factual data only. "
            "Never fabricate experience. Return ONLY valid JSON."
        )

        raw_response = self.ai.generate_text(
            prompt,
            system_instruction=system_instruction,
            json_mode=True,
        )

        # Parse → Validate → Merge
        parsed = self._parse_ai_response(raw_response)
        if parsed:
            optimized = self._merge_optimization(optimized, parsed)
            optimized["_optimization_status"] = "applied"
            optimized["_active_provider"] = self.ai.active_provider
        else:
            optimized["_optimization_status"] = "fallback"
            optimized["_raw_ai_response"] = raw_response

        return optimized

    # ── Private helpers ──────────────────────────────────────────────

    @staticmethod
    def _parse_ai_response(response: str) -> OptimizedOutput | None:
        """Extracts JSON → validates against OptimizedOutput model."""
        if not response or response.startswith("[AI Error]"):
            return None

        try:
            # Strip markdown code fences if the model wrapped the JSON
            json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", response)
            json_str = json_match.group(1).strip() if json_match else response.strip()
            data = json.loads(json_str)
            return OptimizedOutput(**data)
        except (json.JSONDecodeError, Exception):
            return None

    @staticmethod
    def _merge_optimization(resume: dict, opt: OptimizedOutput) -> dict:
        """Merges validated optimised content back into the resume dict."""

        # ── Summary ──────────────────────────────────────────────────
        if opt.summary:
            resume["summary"] = opt.summary

        # ── Experience highlights ────────────────────────────────────
        for opt_exp in opt.experience:
            for orig_exp in resume.get("experience", []):
                if (
                    orig_exp.get("company", "").lower().strip()
                    == opt_exp.company.lower().strip()
                ):
                    if opt_exp.highlights:
                        orig_exp["highlights"] = opt_exp.highlights
                    break

        # ── Project highlights ───────────────────────────────────────
        for project in resume.get("projects", []):
            title = project.get("title", "")
            if title in opt.project_highlights:
                project["highlights"] = opt.project_highlights[title]

        # ── Skills emphasis metadata ─────────────────────────────────
        if opt.skills_to_emphasize:
            resume.setdefault("_optimization_meta", {})[
                "emphasized_skills"
            ] = opt.skills_to_emphasize

        return resume
