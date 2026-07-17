import os
import tempfile
import json
from src.utils.helpers import load_json_file, save_json_file


def test_load_json_file_not_found():
    result = load_json_file("/nonexistent/path.json")
    assert result == {}


def test_load_json_file_invalid():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("not valid json")
        path = f.name
    try:
        result = load_json_file(path)
        assert result == {}
    finally:
        os.unlink(path)


def test_save_and_load_json_file():
    data = {"name": "test", "skills": ["python"]}
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test.json")
        assert save_json_file(path, data) is True
        loaded = load_json_file(path)
        assert loaded == data


def test_load_json_file_empty():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("{}")
        path = f.name
    try:
        result = load_json_file(path)
        assert result == {}
    finally:
        os.unlink(path)
