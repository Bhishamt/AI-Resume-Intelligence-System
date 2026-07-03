from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ProjectRanker:
    @staticmethod
    def rank_projects(projects: list, job_desc: str) -> list:
        """Ranks projects based on semantic overlap with the job description."""
        if not projects or not job_desc:
            return projects
            
        ranked = []
        vectorizer = TfidfVectorizer(stop_words='english')
        
        for project in projects:
            project_text = f"{project.get('title', '')} {project.get('description', '')} {' '.join(project.get('technologies', []))}"
            try:
                tfidf = vectorizer.fit_transform([project_text, job_desc])
                score = float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0])
            except Exception:
                score = 0.0
            
            project_copy = project.copy()
            project_copy["relevance_score"] = round(score, 3)
            ranked.append(project_copy)
            
        # Sort descending by relevance score
        ranked.sort(key=lambda x: x.get("relevance_score", 0.0), reverse=True)
        return ranked
