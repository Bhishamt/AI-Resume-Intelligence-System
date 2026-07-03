"""
AI Resume Intelligence System — Streamlit Dashboard
Automated Career Intelligence Engine for Candidate Name
"""

import streamlit as st
import os
import sys
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.config import Config
from src.utils.helpers import load_json_file
from src.ats.keyword_extractor import KeywordExtractor
from src.ats.ats_scorer import ATSScorer
from src.ats.skill_gap import SkillGapAnalyzer
from src.resume.resume_generator import ResumeGenerator
from src.resume.cover_letter import CoverLetterGenerator
from src.resume.project_ranker import ProjectRanker
from src.resume.persona_selector import PersonaSelector
from src.parser.company_analyzer import CompanyAnalyzer
from src.parser.job_parser import JobParser
from src.export.pdf_export import PDFExporter
from src.export.docx_export import DOCXExporter
from src.security.prompt_sanitizer import PromptSanitizer
from src.versioning.history import ExportHistory
from src.ai.provider import AIProvider

# ═══════════════════════════════════════════════════════════════════════
# Page config
# ═══════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Career Intelligence Engine",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    .stApp { background: radial-gradient(circle at top right, #1f1b2c, #0d0c15 60%); color: #f1f1f1; }
    .title-gradient {
        background: linear-gradient(135deg, #a78bfa 0%, #6366f1 50%, #3b82f6 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 3rem; margin-bottom: 0.2rem;
    }
    .subtitle { color: #9ca3af; font-size: 1.15rem; margin-bottom: 2rem; }
    .glass-card {
        background: rgba(30, 27, 46, 0.45); backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px;
        padding: 24px; margin-bottom: 20px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    .metric-value { font-size: 2.5rem; font-weight: 800; color: #a78bfa; margin: 5px 0; }
    .metric-label { font-size: 0.85rem; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.1em; }
    div.stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #3b82f6 100%);
        color: white; border: none; border-radius: 8px; padding: 10px 24px;
        font-weight: 600; width: 100%;
    }
    .relevance-high { color: #22c55e; font-weight: 700; }
    .relevance-mid  { color: #f59e0b; font-weight: 700; }
    .relevance-low  { color: #ef4444; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_ai_provider():
    provider = AIProvider()
    provider.run_health_checks()
    return provider

ai_provider = get_ai_provider()
extractor = KeywordExtractor()
generator = ResumeGenerator(ai_provider)
cl_generator = CoverLetterGenerator(ai_provider)
ranker = ProjectRanker()
company_intel = CompanyAnalyzer()

st.markdown('<div class="title-gradient">Career Intelligence Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Automated ATS Optimization Pipeline for Candidate Name</div>', unsafe_allow_html=True)

st.sidebar.markdown("### 💼 Career Intelligence Suite")
st.sidebar.markdown("#### 🟢 AI Provider Status")
for name, status in ai_provider.status.items():
    color = "🟢" if status == "healthy" else "🔴" if "error" in status else "🟡"
    st.sidebar.markdown(f"{color} **{name.title()}**: {status}")

# Initialize session state for results
if "pipeline_complete" not in st.session_state:
    st.session_state["pipeline_complete"] = False
    
from src.parser.synthetic_jd_generator import SyntheticJDGenerator

# ═══════════════════════════════════════════════════════════════════════
# Input Section
# ═══════════════════════════════════════════════════════════════════════
st.markdown('<div class="glass-card"><h3>Target Job Details (Triple Input Mode)</h3></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Mode 1: Job URL", "Mode 2: Manual Job", "Mode 3: Full JD Paste"])

with tab1:
    job_url = st.text_input("Job URL (LinkedIn, Naukri, Indeed, Company Careers)", placeholder="https://www.linkedin.com/jobs/view/xxxx", key="url_input")
    mode1_btn = st.button("Generate from URL", key="btn_mode1")

with tab2:
    manual_title = st.text_input("Job Title (Required)", placeholder="Software Developer Intern", key="man_title")
    manual_company = st.text_input("Company Name (Required)", placeholder="Infrabyte Consulting", key="man_company")
    manual_location = st.text_input("Location (Optional)", placeholder="Remote - India", key="man_loc")
    manual_desc = st.text_area("Optional Context", placeholder="Any other details...", key="man_desc")
    mode2_btn = st.button("Generate from Manual Entry", key="btn_mode2")

with tab3:
    full_jd_text = st.text_area("Full Job Description Paste", height=250, key="paste_input")
    mode3_btn = st.button("Generate from Paste", key="btn_mode3")

active_mode = None
if mode1_btn: active_mode = 1
elif mode2_btn: active_mode = 2
elif mode3_btn: active_mode = 3

if active_mode:
    st.session_state["pipeline_complete"] = False
    
    with st.status("🚀 Running Automated Intelligence Pipeline...", expanded=True) as status:
        if active_mode == 1:
            st.write("1. Parsing Job Description from URL...")
            if not job_url.strip():
                status.update(label="Validation Failed", state="error")
                st.error("Please provide a Job URL.")
                st.stop()
            parsed = JobParser.parse_url(job_url.strip())
            if "error" in parsed:
                status.update(label="Scraping Failed", state="error")
                st.error(f"{parsed['error']} | Please try Mode 2 (Manual) or Mode 3 (Full Paste).")
                st.stop()
            raw_text = parsed.get("raw_text", "")
            target_company = parsed.get("company", "Unknown Company")
            target_job_title = parsed.get("title", "Target Role")
            
        elif active_mode == 2:
            st.write("1. Inferring Job Description using AI...")
            if not manual_title.strip() or not manual_company.strip():
                status.update(label="Validation Failed", state="error")
                st.error("Job Title and Company Name are required for Mode 2.")
                st.stop()
            target_job_title = manual_title.strip()
            target_company = manual_company.strip()
            raw_text = SyntheticJDGenerator.generate(
                job_title=target_job_title,
                company=target_company,
                location=manual_location.strip(),
                partial_desc=manual_desc.strip(),
                ai_provider=ai_provider
            )
            
        elif active_mode == 3:
            st.write("1. Parsing Pasted Job Description...")
            if not full_jd_text.strip():
                status.update(label="Validation Failed", state="error")
                st.error("Please paste the job description text.")
                st.stop()
            parsed = JobParser.parse_raw_text(full_jd_text.strip())
            raw_text = parsed.get("raw_text", "")
            target_company = parsed.get("company", "Unknown Company")
            target_job_title = parsed.get("title", "Target Role")

        clean_text, warnings = PromptSanitizer.sanitize(raw_text)
        if not clean_text:
            status.update(label="Parsing Failed", state="error")
            st.error("Could not extract valid job description text.")
            st.stop()
            
        st.write("2. Analyzing Company Intel...")
        company_report = company_intel.analyze(target_company)
        
        st.write("3. Loading Candidate Profile (Candidate Name)...")
        profile = load_json_file(os.path.join("data", "profile.local.json"))
        
        st.write("4. Extracting Keywords & Selecting Persona...")
        extracted = extractor.extract_keywords(clean_text)
        all_kw = extracted["programming_languages"] + extracted["frameworks_libraries"] + extracted["concepts"]
        persona = PersonaSelector.select_best_persona(clean_text)
        
        st.write("5. Running ATS & Skill Gap Analysis...")
        cand_skills = []
        for v in profile.get("skills", {}).values(): 
            cand_skills.extend(v)
            
        gap_analysis = SkillGapAnalyzer.analyze_gaps(cand_skills, all_kw)
        missing_skills = gap_analysis["missing_skills"]
        
        flat_resume = f"{profile.get('summary', '')} " + " ".join(cand_skills)
        ats_results = ATSScorer.calculate_score(flat_resume, clean_text, cand_skills, all_kw)
        
        st.write("6. Ranking Projects...")
        ranked_projects = ranker.rank_projects(profile.get("projects", []), clean_text)
        
        st.write(f"7. Optimizing Resume (Persona: {persona.get('name')})...")
        optimized_resume = generator.generate_optimized_resume(clean_text, all_kw, persona=persona)
        
        st.write("8. Drafting Cover Letter...")
        cover_letter = cl_generator.generate(profile, clean_text, persona=persona)
        
        st.write("9. Exporting Documents & Logging to Database...")
        export_dir = Config.OUTPUT_DIR
        os.makedirs(export_dir, exist_ok=True)
        pdf_path = os.path.join(export_dir, "optimized_resume.pdf")
        docx_path = os.path.join(export_dir, "optimized_resume.docx")
        cl_path = os.path.join(export_dir, "cover_letter.pdf")
        
        PDFExporter.export(optimized_resume, pdf_path)
        DOCXExporter.export(optimized_resume, docx_path)
        PDFExporter.export_cover_letter(cover_letter, optimized_resume.get("personal_info", {}), target_company, cl_path)
        
        # Save to DB
        history_entry = ExportHistory.save_generation(
            company=target_company,
            job_title=target_job_title,
            raw_text=clean_text,
            persona=persona.get("name", "Software Developer"),
            ats_score=ats_results["score"],
            recruiter_score=ats_results["recruiter_score"],
            keyword_match_pct=ats_results["keyword_match_pct"],
            missing_skills=missing_skills,
            recommended_skills=gap_analysis.get("recommended_courses", []),
            ranked_projects=ranked_projects,
            exported_files=[pdf_path, docx_path, cl_path]
        )
        
        # Store results in session state
        st.session_state.update({
            "target_company": target_company,
            "target_job_title": target_job_title,
            "company_report": company_report,
            "ats_results": ats_results,
            "missing_skills": missing_skills,
            "ranked_projects": ranked_projects,
            "persona": persona,
            "optimized_resume": optimized_resume,
            "cover_letter": cover_letter,
            "pdf_path": pdf_path,
            "docx_path": docx_path,
            "cl_path": cl_path,
            "pipeline_complete": True
        })
        
        status.update(label="Pipeline Complete!", state="complete", expanded=False)

# ═══════════════════════════════════════════════════════════════════════
# Output Section
# ═══════════════════════════════════════════════════════════════════════
if st.session_state["pipeline_complete"]:
    st.markdown("---")
    st.markdown("## Career Intelligence Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'<div class="glass-card"><h3>1. Job Analysis</h3><p><b>Title:</b> {st.session_state["target_job_title"]}</p><p><b>Company:</b> {st.session_state["target_company"]}</p></div>', unsafe_allow_html=True)
        
        rpt = st.session_state["company_report"]
        st.markdown(f'<div class="glass-card"><h3>2. Company Analysis</h3><p>{rpt.get("summary")}</p><b>Culture:</b> {", ".join(rpt.get("culture_keywords", []))}<br><b>Tech Stack:</b> {", ".join(rpt.get("tech_stack_inferred", []))}</div>', unsafe_allow_html=True)
        
    with col2:
        ats = st.session_state["ats_results"]
        st.markdown(f'''
        <div class="glass-card">
            <div style="display: flex; gap: 20px;">
                <div><div class="metric-label">3. ATS Score</div><div class="metric-value">{ats["score"]}%</div></div>
                <div><div class="metric-label">4. Recruiter Score</div><div class="metric-value">{ats["recruiter_score"]}%</div></div>
                <div><div class="metric-label">Keyword Match</div><div class="metric-value">{ats["keyword_match_pct"]}%</div></div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        miss = st.session_state["missing_skills"]
        st.markdown(f'<div class="glass-card"><h3>5. Skill Gap</h3><p>{" | ".join(miss) if miss else "No critical gaps found!"}</p></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="glass-card"><h3>6. Selected Persona</h3><h4 style="color:#a78bfa;">{st.session_state["persona"].get("name")}</h4><p>{st.session_state["persona"].get("description")}</p></div>', unsafe_allow_html=True)
    
    st.markdown("### 7. Project Ranking")
    for i, project in enumerate(st.session_state["ranked_projects"]):
        score = project.get("relevance_score", 0.0)
        score_pct = round(score * 100, 1)
        css_class, badge = ("relevance-high", "🟢 HIGH") if score >= 0.3 else ("relevance-mid", "🟡 MODERATE") if score >= 0.15 else ("relevance-low", "🔴 LOW")
        st.markdown(f'<div class="glass-card"><h4>#{i + 1} — {project.get("title")}</h4><div class="metric-label">Relevance Score</div><div class="{css_class}" style="font-size:1.2rem;">{score_pct}% — {badge}</div></div>', unsafe_allow_html=True)

    st.markdown("### 8. Optimized Resume")
    st.info(st.session_state["optimized_resume"].get("summary", ""))

    st.markdown("### 9. Cover Letter")
    st.text_area("Cover Letter", value=st.session_state["cover_letter"], height=300, disabled=True)

    st.markdown("### 10. Export Links")
    d1, d2, d3 = st.columns(3)
    with d1:
        with open(st.session_state["pdf_path"], "rb") as f:
            st.download_button("Download PDF Resume", f, "Candidate_Resume.pdf", "application/pdf")
    with d2:
        with open(st.session_state["docx_path"], "rb") as f:
            st.download_button("Download DOCX Resume", f, "Candidate_Resume.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    with d3:
        with open(st.session_state["cl_path"], "rb") as f:
            st.download_button("Download Cover Letter", f, "Candidate_CoverLetter.pdf", "application/pdf")

    st.markdown("### 11. Version History")
    manifest_path = os.path.join(Config.OUTPUT_DIR, "history", "manifest.json")
    if os.path.exists(manifest_path):
        try:
            import json, pandas as pd
            with open(manifest_path, "r", encoding="utf-8") as mf:
                manifest_data = json.load(mf)
                st.dataframe(pd.DataFrame(manifest_data).tail(10))
        except Exception:
            st.write("Unable to load version history.")
    else:
        st.write("No version history yet.")
