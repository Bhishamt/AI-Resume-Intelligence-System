class SkillGapAnalyzer:
    @staticmethod
    def analyze_gaps(resume_skills: list, job_keywords: list) -> dict:
        """Finds skills present in job description but missing in user profile."""
        resume_skills_set = {s.lower().strip() for s in resume_skills}
        job_keywords_set = {k.lower().strip() for k in job_keywords}
        
        missing_skills = list(job_keywords_set - resume_skills_set)
        matching_skills = list(job_keywords_set & resume_skills_set)
        
        # Recommendations
        recommendations = []
        for skill in missing_skills:
            recommendations.append(f"Consider learning or adding relevant project work in '{skill.capitalize()}' if you have experience.")

        return {
            "matching_skills": [s.capitalize() for s in matching_skills],
            "missing_skills": [s.capitalize() for s in missing_skills],
            "recommendations": recommendations
        }
