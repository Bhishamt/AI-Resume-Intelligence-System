import os
import json
import logging

logger = logging.getLogger(__name__)

def load_json_file(file_path: str) -> dict:
    """Safely loads a JSON file from disk."""
    if not os.path.exists(file_path):
        return {}
    try:
        with open(file_path) as f:
            return json.load(f)
    except Exception as e:
        logger.error("Error loading %s: %s", file_path, e)
        return {}

def save_json_file(file_path: str, data: dict) -> bool:
    """Safely writes a dictionary to a JSON file on disk."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error("Error saving to %s: %s", file_path, e)
        return False
