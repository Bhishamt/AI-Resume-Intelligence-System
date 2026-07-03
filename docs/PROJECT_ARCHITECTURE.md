# AI-Resume-Intelligence-System Architecture

## System Architecture
The AI-Resume-Intelligence-System is designed as a modular, AI-powered pipeline to optimize technical resumes against Job Descriptions (JDs) and ATS (Applicant Tracking Systems). 
It employs a robust backend written in Python with a front-end powered by Streamlit, ensuring seamless interaction for the candidate.

## Data Flow
1. **Input Stage:** Candidates supply job details (via URL, Manual Entry, or Raw Text Paste).
2. **Analysis Stage:** 
   - Generative AI analyzes the target company culture and technical requirements.
   - The ATS keyword extraction engine processes the raw text to identify key programming languages, frameworks, and concepts.
3. **Evaluation Stage:** The candidate's master resume is scored against the extracted keywords, generating an ATS match percentage, skill gap report, and recruiter score.
4. **Generation Stage:** A dynamic persona is matched to the JD, and optimized PDF/DOCX resumes and cover letters are generated.
5. **Storage Stage:** The generated artifacts and metadata are recorded in `exports/history/` for version tracking.

## Triple Input Mode Workflow
To handle the diverse formatting of modern job postings, the engine utilizes a Triple Input Mode:
- **Mode 1 (Job URL):** Employs scraping tools to extract raw data directly from LinkedIn, Indeed, etc.
- **Mode 2 (Manual Job):** Generates synthetic job description inferences based on Company and Job Title using the LLM.
- **Mode 3 (Full JD Paste):** A direct bypass for complex JDs, applying prompt sanitization before keyword extraction.

## ATS Optimization Pipeline
1. **Prompt Sanitization:** Strips garbage characters and handles edge-case unicode from JDs.
2. **Keyword Extraction:** Identifies hard technical constraints (Languages/Frameworks) vs soft skills.
3. **Skill Gap Analysis:** Highlights critical missing skills and recommends potential courses or certifications.
4. **Project Ranking:** Dynamically orders candidate projects based on vector relevance to the job requirements.
5. **Document Export:** Generates clean, ATS-readable PDF and DOCX files.
