from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

class ATSScorer:
    @staticmethod
    def calculate_score(resume_text: str, job_desc_text: str, candidate_skills: list = None, extracted_keywords: list = None) -> dict:
        """Calculates ATS match score, recruiter score, and keyword match %."""
        if not resume_text or not job_desc_text:
            return {
                "score": 0.0, 
                "recruiter_score": 0.0,
                "keyword_match_pct": 0.0,
                "match_level": "Low", 
                "details": "Empty resume or job description."
            }

        # Compute cosine similarity using TfidfVectorizer for overall ATS Score
        vectorizer = TfidfVectorizer(stop_words='english')
        try:
            tfidf = vectorizer.fit_transform([resume_text, job_desc_text])
            sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
            ats_score = float(np.round(sim * 100, 2))
        except Exception:
            ats_score = 10.0
            
        # Keyword Match Percentage
        keyword_match_pct = 0.0
        if candidate_skills and extracted_keywords:
            c_skills_lower = [s.lower() for s in candidate_skills]
            matches = [k for k in extracted_keywords if k.lower() in c_skills_lower]
            keyword_match_pct = float(np.round((len(matches) / max(len(extracted_keywords), 1)) * 100, 2))
            
        # Recruiter Score Heuristic (combines ATS relevance with Keyword match)
        recruiter_score = float(np.round((ats_score * 0.4) + (keyword_match_pct * 0.6), 2))
            
        if ats_score >= 80:
            match_level = "Excellent"
        elif ats_score >= 60:
            match_level = "Good"
        elif ats_score >= 40:
            match_level = "Fair"
        else:
            match_level = "Low"

        return {
            "score": ats_score,
            "recruiter_score": recruiter_score,
            "keyword_match_pct": keyword_match_pct,
            "match_level": match_level,
            "details": f"Your resume has a {match_level.lower()} semantic overlap ({ats_score}%) with the target job role."
        }
