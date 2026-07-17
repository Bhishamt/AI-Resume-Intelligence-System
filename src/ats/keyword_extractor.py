import json
import re
from src.utils.config import Config
from src.utils.helpers import load_json_file

class KeywordExtractor:
    def __init__(self):
        self.keywords_db = load_json_file(Config.ATS_KEYWORDS_PATH)

    def extract_keywords(self, text: str) -> dict:
        """Extracts known keywords and matches synonyms in the text."""
        extracted = {
            "programming_languages": [],
            "frameworks_libraries": [],
            "concepts": []
        }
        
        text_lower = text.lower()
        
        for category, mappings in self.keywords_db.items():
            for key, synonyms in mappings.items():
                for synonym in synonyms:
                    pattern = rf"\b{re.escape(synonym)}\b"
                    if re.search(pattern, text_lower):
                        if category in extracted:
                            extracted[category].append(key)
                            break  # Avoid adding duplicates from multiple synonyms
                            
        return extracted
