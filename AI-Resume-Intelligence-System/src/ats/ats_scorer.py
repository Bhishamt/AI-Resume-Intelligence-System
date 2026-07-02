from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class ATSScorer:
    @staticmethod
    def calculate_score(resume_text: str, job_desc_text: str) -> dict:
        """Calculates ATS match score using semantic cosine similarity and recruiter heuristic rules."""
        if not resume_text or not job_desc_text:
            return {"score": 0.0, "match_level": "Low", "details": "Empty resume or job description."}

        # Compute cosine similarity using TfidfVectorizer
        vectorizer = TfidfVectorizer(stop_words='english')
        try:
            tfidf = vectorizer.fit_transform([resume_text, job_desc_text])
            sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
            score = float(np.round(sim * 100, 2))
        except Exception:
            score = 10.0  # Heuristic fallback if Vectorizer fails
            
        if score >= 80:
            match_level = "Excellent"
        elif score >= 60:
            match_level = "Good"
        elif score >= 40:
            match_level = "Fair"
        else:
            match_level = "Low"

        return {
            "score": score,
            "match_level": match_level,
            "details": f"Your resume has a {match_level.lower()} semantic overlap ({score}%) with the target job role."
        }
