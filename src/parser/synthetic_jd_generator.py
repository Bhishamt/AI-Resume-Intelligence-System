"""
Synthetic Job Description Generator for Manual Mode (Mode 2)
Generates a comprehensive job description based on minimal inputs (Job Title and Company).
"""

from src.ai.provider import AIProvider
from src.security.prompt_sanitizer import PromptSanitizer

class SyntheticJDGenerator:
    """Generates a synthetic job description from minimal inputs using AI."""
    
    @staticmethod
    def generate(job_title: str, company: str, location: str = "", partial_desc: str = "", ai_provider: AIProvider = None) -> str:
        if ai_provider is None:
            ai_provider = AIProvider()
            
        prompt = f"""
        You are an expert technical recruiter and hiring manager at {company}.
        I need you to write a highly realistic and comprehensive Job Description for the following role:
        
        Job Title: {job_title}
        Company: {company}
        Location: {location if location else 'Remote or Undisclosed'}
        Additional Context: {partial_desc if partial_desc else 'None'}
        
        The generated job description MUST include:
        1. A brief overview of the role and company (inferred based on the company name).
        2. Detailed Responsibilities.
        3. Required Skills and Qualifications (Hard skills, programming languages, frameworks, tools).
        4. Preferred/Bonus Skills.
        5. Common ATS keywords and hidden recruiter intent keywords for this specific role and industry.
        
        Format the output clearly with headings. 
        Do not include introductory conversational text, just output the raw Job Description text.
        """
        
        response = ai_provider.generate_content(prompt)
        if not response:
            return ""
            
        # Ensure it's clean text
        clean_text, _ = PromptSanitizer.sanitize(response)
        return clean_text
