# System Architecture

The AI Resume Intelligence System is designed to process and optimize resumes according to modern ATS (Applicant Tracking System) standards, leveraging Large Language Models (LLMs).

## Core Components

### 1. Triple Input Mode
The system supports three distinct methods for ingesting Job Descriptions (JD):
*   **Mode 1: Job URL:** Automatically fetches and parses the job description from a provided URL.
*   **Mode 2: Manual Job + Company:** Allows users to manually input the job title, company name, and key requirements.
*   **Mode 3: Full Job Description:** Users can paste the entire raw text of a job description for comprehensive analysis.

### 2. ATS Pipeline
The ATS Pipeline is responsible for:
*   **Keyword Extraction:** Identifying essential hard skills, soft skills, and action verbs from the JD.
*   **Format Compliance:** Ensuring the resume structure adheres to ATS-friendly formats (e.g., standard headings, single-column layout).
*   **Scoring:** Evaluating the initial resume against the JD to provide a baseline ATS score.

### 3. Resume Generation Flow
The generation process follows these steps:
1.  **Ingestion:** Parse user profile (skills, experience, projects) and the target JD.
2.  **Persona Matching:** Select an appropriate professional persona (e.g., Backend Developer, Data Scientist) to guide the tone and focus of the resume.
3.  **Content Optimization:** Rewrite bullet points using the STAR method, injecting ATS keywords naturally.
4.  **Project Ranking:** Reorder and select the most relevant projects based on the JD requirements.
5.  **Output:** Export the finalized resume in standard formats (Markdown, PDF, DOCX).
