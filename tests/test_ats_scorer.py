import pytest
from src.ats.ats_scorer import ATSScorer


def test_calculate_score_returns_dict():
    resume = "Python Django developer"
    jd = "Looking for Django engineers"
    result = ATSScorer.calculate_score(resume, jd)
    assert isinstance(result, dict)
    assert "score" in result
    assert "recruiter_score" in result
    assert "keyword_match_pct" in result
    assert "match_level" in result


def test_calculate_score_empty_input():
    result = ATSScorer.calculate_score("", "")
    assert result["score"] >= 0
    assert result["match_level"] in ["Low", "Fair", "Good", "Excellent"]


def test_calculate_score_high_match():
    resume = "Python Django React PostgreSQL AWS developer with 5 years experience"
    jd = "We need a Python Django React PostgreSQL AWS engineer"
    result = ATSScorer.calculate_score(resume, jd)
    assert result["score"] > 0
    assert result["keyword_match_pct"] >= 0


def test_calculate_score_with_skills():
    resume = "Python developer"
    jd = "Seeking Python and Rust engineers"
    result = ATSScorer.calculate_score(resume, jd, candidate_skills=["Python"], extracted_keywords=["Python", "Rust"])
    assert result["keyword_match_pct"] == 50.0
