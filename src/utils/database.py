import sqlite3
import os
from src.utils.config import Config

DB_PATH = os.path.join(Config.OUTPUT_DIR, "history", "exports.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table for job_analysis
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT,
            company TEXT,
            raw_text TEXT,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table for generations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS generations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            persona TEXT,
            ats_score REAL,
            recruiter_score REAL,
            keyword_match_pct REAL,
            missing_skills TEXT,
            recommended_skills TEXT,
            files_exported TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES job_analysis(id)
        )
    ''')
    
    # Table for project_rankings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_rankings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            generation_id INTEGER,
            project_title TEXT,
            relevance_score REAL,
            FOREIGN KEY (generation_id) REFERENCES generations(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_PATH)

# Initialize database on module import
init_db()
