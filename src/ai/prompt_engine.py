"""
Prompt engineering templates for the AI Resume Intelligence System.

All prompts embed CRITICAL CONSTRAINTS that prevent hallucination:
  - Never fabricate experience, credentials, or education.
  - Only optimise phrasing, structure, and keyword alignment.
  - Resume optimisation prompt requests structured JSON from the LLM.
  - Persona context is injected when a matching role template is found.
"""

import json


class PromptEngine:
    @staticmethod
    def get_system_constraints() -> str:
        return (
            "CRITICAL CONSTRAINTS:\n"
            "1. NEVER generate fake experience or fabricate job history.\n"
            "2. NEVER generate fake certifications or education.\n"
            "3. Preserve absolute factual accuracy of the provided candidate profile.\n"
            "4. Only optimize phrasing, vocabulary, structure, and keyword alignment based on facts."
        )

    @classmethod
    def build_resume_optimization_prompt(
        cls,
        master_profile: dict,
        job_description: str,
        target_keywords: list,
        persona: dict | None = None,
    ) -> str:
        constraints = cls.get_system_constraints()

        persona_block = ""
        if persona:
            persona_block = (
                f"\n\n=== ROLE PERSONA: {persona.get('name', 'General')} ===\n"
                f"Tone: {persona.get('tone', 'Professional and results-oriented')}\n"
                f"Emphasise: {', '.join(persona.get('emphasis_areas', []))}\n"
                f"Priority skills: {', '.join(persona.get('priority_skills', []))}\n"
            )

        return (
            f"{constraints}\n\n"
            f"You are an expert resume optimizer and ATS specialist.\n"
            f"{persona_block}\n"
            f"=== CANDIDATE MASTER PROFILE ===\n"
            f"{json.dumps(master_profile, indent=2)}\n\n"
            f"=== TARGET JOB DESCRIPTION ===\n"
            f"{job_description}\n\n"
            f"=== TARGET KEYWORDS ===\n"
            f"{', '.join(target_keywords)}\n\n"
            f"TASK: Optimise the candidate's summary and experience highlights "
            f"to maximise ATS match rate for this job. Naturally incorporate "
            f"target keywords where truthful. Keep all facts accurate.\n\n"
            f"Return your response as a single valid JSON object with this "
            f"exact structure (no markdown, no code fences, ONLY JSON):\n\n"
            f'{{\n'
            f'  "summary": "optimised professional summary text",\n'
            f'  "experience": [\n'
            f'    {{\n'
            f'      "job_title": "exact original job title",\n'
            f'      "company": "exact original company name",\n'
            f'      "highlights": [\n'
            f'        "optimised bullet point 1",\n'
            f'        "optimised bullet point 2"\n'
            f'      ]\n'
            f'    }}\n'
            f'  ],\n'
            f'  "skills_to_emphasize": ["skill1", "skill2"],\n'
            f'  "project_highlights": {{\n'
            f'    "Exact Project Title": ["optimised highlight"]\n'
            f'  }}\n'
            f'}}\n'
        )

    @classmethod
    def build_cover_letter_prompt(
        cls,
        master_profile: dict,
        job_description: str,
        persona: dict | None = None,
    ) -> str:
        constraints = cls.get_system_constraints()

        tone_hint = ""
        if persona:
            tone_hint = f"\nTone guidance: {persona.get('tone', '')}\n"

        return (
            f"{constraints}\n\n"
            f"You are a professional career writer.\n"
            f"{tone_hint}\n"
            f"Write a highly tailored cover letter based on the following "
            f"Master Profile:\n{json.dumps(master_profile, indent=2)}\n\n"
            f"And target Job Description:\n{job_description}\n\n"
            f"Requirements:\n"
            f"- Do NOT fabricate any roles, metrics, or credentials.\n"
            f"- Write 3-4 professional paragraphs.\n"
            f"- Highlight matching projects and real experience.\n"
            f"- Use a confident, professional tone."
        )
