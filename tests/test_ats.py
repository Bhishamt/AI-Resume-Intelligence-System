import pytest
from src.ats.keyword_extractor import KeywordExtractor
from src.ats.ats_scorer import ATSScorer
from src.ats.skill_gap import SkillGapAnalyzer

def test_keyword_extraction():
    extractor = KeywordExtractor()
    # Mock database is loaded. Let's test matches
    text = "We need a Python developer who knows Django and React."
    keywords = extractor.extract_keywords(text)
    
    assert "Python" in keywords["programming_languages"]
    assert "Django" in keywords["frameworks_libraries"]
    assert "React" in keywords["frameworks_libraries"]

def test_ats_scorer():
    resume = "Python Django developer with 4 years experience."
    job_desc = "Seeking Django and Python engineers."
    
    score_res = ATSScorer.calculate_score(resume, job_desc)
    assert score_res["score"] > 0
    assert score_res["match_level"] in ["Low", "Fair", "Good", "Excellent"]

def test_skill_gap():
    resume_skills = ["Python", "Django"]
    job_keywords = ["Python", "Django", "AWS", "React"]
    
    gap_report = SkillGapAnalyzer.analyze_gaps(resume_skills, job_keywords)
    
    assert "aws" in gap_report["missing_skills"]
    assert "react" in gap_report["missing_skills"]
    assert "python" in gap_report["matching_skills"]
