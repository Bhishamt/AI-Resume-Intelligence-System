# AI-Resume-Intelligence-System

An AI-powered ATS Resume Optimization and Career Intelligence System that automatically generates optimized resumes and cover letters based on a user's master profile and a target job description.

## 🚀 Features

- **Master Resume Profile**: Centralized, schema-validated storage for your career history (experiences, education, skills, certifications).
- **ATS Keyword Extractor & Matcher**: Deep-scrapes target job postings to identify required hard skills, soft skills, and key phrases.
- **ATS Score Predictor**: Uses semantic text matching to score your resume relevance against the job description.
- **Skill Gap Analyzer**: Highlights missing skills and lists recommendations for course topics or profile enrichment.
- **AI-Powered Resume Optimizer**: Tailors achievements and bullet points to emphasize relevant skills without fabricating experience.
- **Cover Letter Generator**: Drafts customized cover letters highlighting matching projects and experiences.
- **Project Ranking Engine**: Selects and sorts your top projects based on relevance to the job.
- **Multiformat Exports**: Download customized resumes in high-quality PDF or editable DOCX formats.

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI Models**: Gemini API (Free Tier), Groq API (Fallback)
- **Data Scraping**: Playwright & BeautifulSoup4
- **Document Generation**: ReportLab (PDF), python-docx (DOCX)
- **ML / Analysis**: pandas, scikit-learn, sentence-transformers
- **Database**: Local JSON Database (`data/master_resume.json`)

## ⚙️ Setup and Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/AI-Resume-Intelligence-System.git
   cd AI-Resume-Intelligence-System
   ```

2. **Create a virtual environment and install dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Install Playwright Browsers**:
   ```bash
   playwright install
   ```

4. **Configure environment variables**:
   Create a `.env` file in the root directory and add your keys:
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   GROQ_API_KEY=your_groq_api_key
   ```

5. **Run the Streamlit application**:
   ```bash
   streamlit run ui/streamlit_app.py
   ```

## 🔒 Factual Integrity Constraints
This project adheres to strict validation rules:
- **Never generate fake experience.**
- **Never generate fake certifications.**
- **Never generate fake education.**
- Preserves exact factual accuracy while optimizing word choice and structural organization for ATS match rates.
