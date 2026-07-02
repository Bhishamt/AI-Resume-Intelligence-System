"""
AI Resume Intelligence System — Streamlit Dashboard

Tabs:
  1. Master Profile     – view / edit profile data
  2. ATS & Gap Analysis – keyword extraction, ATS scoring, skill gaps
  3. Project Ranking    – rank projects by relevance to the job
  4. Company Intel      – company culture, tech stack, hiring signals
  5. Cover Letter       – AI-generated tailored cover letter
  6. Export             – PDF / DOCX downloads and versioning history
"""

import streamlit as st
import os
import sys

# Add project root to path so `src.*` imports resolve
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.config import Config
from src.utils.helpers import load_json_file, save_json_file
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
    page_title="AI Resume Intelligence & ATS Optimizer",
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
        transition: transform 0.3s ease, border 0.3s ease;
    }
    .glass-card:hover { transform: translateY(-4px); border: 1px solid rgba(99, 102, 241, 0.3); }
    .metric-value { font-size: 2.5rem; font-weight: 800; color: #a78bfa; margin: 5px 0; }
    .metric-label { font-size: 0.85rem; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.1em; }
    div.stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #3b82f6 100%);
        color: white; border: none; border-radius: 8px; padding: 10px 24px;
        font-weight: 600; transition: all 0.2s ease-in-out; box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #4f46e5 0%, #2563eb 100%);
        transform: scale(1.02); box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
    }
    .relevance-high { color: #22c55e; font-weight: 700; }
    .relevance-mid  { color: #f59e0b; font-weight: 700; }
    .relevance-low  { color: #ef4444; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# Engine Init & Sidebar
# ═══════════════════════════════════════════════════════════════════════
@st.cache_resource
def get_ai_provider():
    provider = AIProvider()
    provider.run_health_checks()
    return provider

ai_provider    = get_ai_provider()
extractor      = KeywordExtractor()
generator      = ResumeGenerator(ai_provider)
cl_generator   = CoverLetterGenerator(ai_provider)
ranker         = ProjectRanker()
company_intel  = CompanyAnalyzer()

st.markdown('<div class="title-gradient">AI Resume Intelligence System</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Production-Ready ATS Optimizer & Pipeline</div>', unsafe_allow_html=True)

for w in Config.validate():
    st.sidebar.warning(w)

st.sidebar.markdown("### 💼 Career Intelligence Suite")
st.sidebar.markdown(f"**Mode:** `{Config.APP_MODE.upper()}`")

st.sidebar.markdown("#### 🟢 AI Provider Status")
for name, status in ai_provider.status.items():
    color = "🟢" if status == "healthy" else "🔴" if "error" in status else "🟡"
    st.sidebar.markdown(f"{color} **{name.title()}**: {status}")

# ── Session state defaults ───────────────────────────────────────────
master_resume = load_json_file(Config.MASTER_RESUME_PATH)
_defaults = {
    "optimized_resume":  master_resume,
    "cover_letter_text": "",
    "ats_score_results": None,
    "missing_skills":    [],
    "ranked_projects":   [],
    "company_report":    None,
    "job_desc_global":   "",
    "active_persona":    None,
    "target_company":    "Unknown Company",
    "target_job_title":  "Target Role",
}
for key, val in _defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ═══════════════════════════════════════════════════════════════════════
# Tabs
# ═══════════════════════════════════════════════════════════════════════
(
    tab_profile,
    tab_optimize,
    tab_projects,
    tab_company,
    tab_letters,
    tab_export,
) = st.tabs([
    "📂 Master Profile",
    "⚡ ATS & Gap Analysis",
    "🏗️ Project Ranking",
    "🏢 Company Intel",
    "📝 Cover Letter",
    "💾 Export",
])

# ═══════════════════════════════════════════════════════════════════════
# 📂 Master Profile
# ═══════════════════════════════════════════════════════════════════════
with tab_profile:
    st.markdown('<div class="glass-card"><h3>Configure Master Resume Profile</h3></div>', unsafe_allow_html=True)
    if master_resume:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Personal & Contact Info")
            personal  = master_resume.get("personal_info", {})
            full_name = st.text_input("Full Name", value=personal.get("full_name", ""))
            email     = st.text_input("Email",     value=personal.get("email", ""))
            phone     = st.text_input("Phone",     value=personal.get("phone", ""))
            location  = st.text_input("Location",  value=personal.get("location", ""))
            website   = st.text_input("Website",   value=personal.get("website", ""))
            st.markdown("#### Professional Summary")
            summary = st.text_area("Master Summary", value=master_resume.get("summary", ""), height=150)
        with col2:
            st.markdown("#### Technical & Professional Skills")
            skills = master_resume.get("skills", {})
            languages = st.text_area("Programming Languages", value=", ".join(skills.get("languages", [])), height=60)
            frameworks = st.text_area("Frameworks/Libraries", value=", ".join(skills.get("frameworks", [])), height=60)
            databases = st.text_area("Databases", value=", ".join(skills.get("databases", [])), height=60)
            tools_platforms = st.text_area("Tools/Platforms", value=", ".join(skills.get("tools_platforms", [])), height=60)

        if st.button("Save Master Profile Updates"):
            master_resume["personal_info"] = {
                "full_name": full_name, "email": email, "phone": phone, "location": location, "website": website,
            }
            master_resume["summary"] = summary
            master_resume["skills"] = {
                "languages": [s.strip() for s in languages.split(",") if s.strip()],
                "frameworks": [s.strip() for s in frameworks.split(",") if s.strip()],
                "databases": [s.strip() for s in databases.split(",") if s.strip()],
                "tools_platforms": [s.strip() for s in tools_platforms.split(",") if s.strip()],
            }
            save_json_file(Config.MASTER_RESUME_PATH, master_resume)
            st.success("Master profile updated successfully!")

# ═══════════════════════════════════════════════════════════════════════
# ⚡ ATS & Gap Analysis
# ═══════════════════════════════════════════════════════════════════════
with tab_optimize:
    st.markdown('<div class="glass-card"><h3>Optimize for Job Posting</h3><p>Paste text or a URL.</p></div>', unsafe_allow_html=True)
    job_desc_input = st.text_area("Job Description or URL", height=150)

    if st.button("Analyze Relevance & Keywords"):
        raw_text = job_desc_input.strip()
        
        if raw_text.startswith("http"):
            with st.spinner("Scraping job URL via Playwright..."):
                parsed = JobParser.parse_url(raw_text)
                if "error" in parsed:
                    st.error(parsed["error"])
                    st.stop()
                raw_text = parsed["raw_text"]
                st.session_state["target_company"] = parsed.get("company", "Unknown")
                st.session_state["target_job_title"] = parsed.get("title", "Target Role")
        else:
            parsed = JobParser.parse_raw_text(raw_text)
            st.session_state["target_company"] = parsed.get("company", "Unknown")
            st.session_state["target_job_title"] = parsed.get("title", "Target Role")

        # Security check
        clean_text, warnings = PromptSanitizer.sanitize(raw_text)
        for w in warnings:
            st.warning(w)

        if not clean_text:
            st.error("Please provide valid job description text.")
        else:
            st.session_state["job_desc_global"] = clean_text

            # Persona selection
            persona = PersonaSelector.select_best_persona(clean_text)
            st.session_state["active_persona"] = persona

            # Extract & score
            extracted = extractor.extract_keywords(clean_text)
            all_kw = extracted["programming_languages"] + extracted["frameworks_libraries"] + extracted["concepts"]
            cand_skills = []
            if master_resume:
                for v in master_resume.get("skills", {}).values(): cand_skills.extend(v)
            
            st.session_state["missing_skills"] = SkillGapAnalyzer.analyze_gaps(cand_skills, all_kw)["missing_skills"]
            
            flat_resume = f"{master_resume.get('summary', '')} " + " ".join(cand_skills)
            for exp in master_resume.get("experience", []):
                flat_resume += f" {exp.get('job_title', '')} {' '.join(exp.get('highlights', []))}"
            st.session_state["ats_score_results"] = ATSScorer.calculate_score(flat_resume, clean_text)

            # Rank projects
            if master_resume.get("projects"):
                st.session_state["ranked_projects"] = ranker.rank_projects(master_resume["projects"], clean_text)

            # AI Optimize
            with st.spinner(f"Optimizing resume using AI (Provider: {ai_provider.active_provider})..."):
                optimized = generator.generate_optimized_resume(clean_text, all_kw, persona=persona)
                st.session_state["optimized_resume"] = optimized

            st.success("Analysis complete!")

    if st.session_state["active_persona"]:
        p_name = st.session_state["active_persona"].get("name")
        st.info(f"🎭 **Active Persona Selected**: {p_name}")

    if st.session_state["ats_score_results"]:
        score_res = st.session_state["ats_score_results"]
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="glass-card"><div class="metric-label">ATS Score</div><div class="metric-value">{score_res["score"]}%</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="glass-card"><div class="metric-label">Match Level</div><div class="metric-value">{score_res["match_level"]}</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="glass-card"><div class="metric-label">Missing Skills</div><div class="metric-value">{len(st.session_state["missing_skills"])}</div></div>', unsafe_allow_html=True)

        if st.session_state["missing_skills"]:
            st.markdown("### 🔍 Skill Gaps")
            for skill in st.session_state["missing_skills"]:
                st.write(f"⚠️ {skill}")

# ═══════════════════════════════════════════════════════════════════════
# 🏗️ Project Ranking
# ═══════════════════════════════════════════════════════════════════════
with tab_projects:
    st.markdown('<div class="glass-card"><h3>Project Relevance Ranking</h3></div>', unsafe_allow_html=True)
    if st.session_state["ranked_projects"]:
        for i, project in enumerate(st.session_state["ranked_projects"]):
            score = project.get("relevance_score", 0.0)
            score_pct = round(score * 100, 1)
            css_class, badge = ("relevance-high", "🟢 HIGH") if score >= 0.3 else ("relevance-mid", "🟡 MODERATE") if score >= 0.15 else ("relevance-low", "🔴 LOW")
            st.markdown(f'<div class="glass-card"><h4>#{i + 1} — {project.get("title", "Untitled")}</h4><div class="metric-label">Relevance Score</div><div class="{css_class}" style="font-size:1.5rem;">{score_pct}% — {badge}</div></div>', unsafe_allow_html=True)
    else:
        st.info("Run ATS analysis first.")

# ═══════════════════════════════════════════════════════════════════════
# 🏢 Company Intelligence
# ═══════════════════════════════════════════════════════════════════════
with tab_company:
    st.markdown('<div class="glass-card"><h3>Company Intelligence</h3></div>', unsafe_allow_html=True)
    company_name_input = st.text_input("Enter Company Name", value=st.session_state.get("target_company", ""))
    if st.button("Analyze Company"):
        if company_name_input.strip():
            with st.spinner("Gathering intelligence..."):
                st.session_state["company_report"] = company_intel.analyze(company_name_input.strip())
    
    if st.session_state["company_report"]:
        rpt = st.session_state["company_report"]
        st.markdown(f'<div class="glass-card"><h3 style="color:#a78bfa;">{rpt.get("company")}</h3><p>{rpt.get("summary")}</p></div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🛠️ Tech Stack")
            for t in rpt.get("tech_stack_inferred", []): st.write(f"• {t}")
        with c2:
            st.markdown("#### 🎯 Culture Keywords")
            for t in rpt.get("culture_keywords", []): st.write(f"• {t}")

# ═══════════════════════════════════════════════════════════════════════
# 📝 Cover Letter
# ═══════════════════════════════════════════════════════════════════════
with tab_letters:
    st.markdown('<div class="glass-card"><h3>Tailored Cover Letter</h3></div>', unsafe_allow_html=True)
    if st.button("Generate Cover Letter with AI"):
        if st.session_state["job_desc_global"]:
            with st.spinner("Drafting cover letter..."):
                st.session_state["cover_letter_text"] = cl_generator.generate(
                    master_resume, 
                    st.session_state["job_desc_global"],
                    persona=st.session_state["active_persona"]
                )
                st.success("Draft generated!")
        else:
            st.error("Analyze a job description first.")

    if st.session_state["cover_letter_text"]:
        st.session_state["cover_letter_text"] = st.text_area("Cover Letter Draft", value=st.session_state["cover_letter_text"], height=300)

# ═══════════════════════════════════════════════════════════════════════
# 💾 Export
# ═══════════════════════════════════════════════════════════════════════
with tab_export:
    st.markdown('<div class="glass-card"><h3>Download Export Bundles & Versioning</h3></div>', unsafe_allow_html=True)
    export_dir = Config.OUTPUT_DIR
    os.makedirs(export_dir, exist_ok=True)
    
    pdf_path = os.path.join(export_dir, "optimized_resume.pdf")
    docx_path = os.path.join(export_dir, "optimized_resume.docx")
    
    col_pdf, col_docx = st.columns(2)
    pdf_success = docx_success = False

    with col_pdf:
        if st.button("Export ATS PDF"):
            if PDFExporter.export(st.session_state["optimized_resume"], pdf_path):
                st.success("PDF generated!")
                pdf_success = True
                with open(pdf_path, "rb") as f:
                    st.download_button("Download PDF", f, "resume.pdf", "application/pdf")
                    
    with col_docx:
        if st.button("Export ATS DOCX"):
            if DOCXExporter.export(st.session_state["optimized_resume"], docx_path):
                st.success("DOCX generated!")
                docx_success = True
                with open(docx_path, "rb") as f:
                    st.download_button("Download DOCX", f, "resume.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    # Version tracking
    st.markdown("---")
    st.markdown("#### Version History Tracker")
    if st.button("Archive Current Exports to History"):
        files = []
        if os.path.exists(pdf_path): files.append(pdf_path)
        if os.path.exists(docx_path): files.append(docx_path)
        if st.session_state.get("cover_letter_text"):
            cl_path = os.path.join(export_dir, "cover_letter.pdf")
            if PDFExporter.export_cover_letter(st.session_state["cover_letter_text"], st.session_state["optimized_resume"].get("personal_info", {}), st.session_state["target_company"], cl_path):
                files.append(cl_path)

        if files:
            score = 0
            if st.session_state["ats_score_results"]:
                score = st.session_state["ats_score_results"]["score"]
            entry = ExportHistory.save_version(
                company=st.session_state["target_company"],
                job_title=st.session_state["target_job_title"],
                ats_score=score,
                exported_files=files
            )
            st.success(f"Archived version v{entry['version']:04d}!")
        else:
            st.warning("Generate some exports first!")
