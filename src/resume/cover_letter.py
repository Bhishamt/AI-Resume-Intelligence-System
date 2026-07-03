from src.ai.prompt_engine import PromptEngine


class CoverLetterGenerator:
    def __init__(self, ai_provider=None):
        if ai_provider is None:
            from src.ai.provider import AIProvider
            ai_provider = AIProvider()
        self.ai = ai_provider

    def generate(self, master_profile: dict, job_desc: str, persona: dict | None = None) -> str:
        """Generates a professional cover letter based on user's profile, job description and persona."""
        prompt = PromptEngine.build_cover_letter_prompt(master_profile, job_desc, persona)
        system_instruction = "Draft a cover letter aligning credentials with role responsibilities. Do not fabricate details."
        return self.ai.generate_text(prompt, system_instruction=system_instruction)
