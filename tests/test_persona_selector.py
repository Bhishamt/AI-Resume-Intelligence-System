import pytest
from src.resume.persona_selector import PersonaSelector


def test_select_best_persona_returns_dict():
    jd = "Looking for a Python developer with Django experience"
    result = PersonaSelector.select_best_persona(jd)
    assert isinstance(result, dict)
    assert "name" in result
    assert "match_keywords" in result


def test_select_best_persona_python():
    jd = "We need a senior Python developer for data engineering"
    result = PersonaSelector.select_best_persona(jd)
    assert result is not None


def test_select_best_persona_frontend():
    jd = "Looking for a React TypeScript frontend engineer"
    result = PersonaSelector.select_best_persona(jd)
    assert result is not None


def test_select_best_persona_fallback():
    result = PersonaSelector.select_best_persona("")
    assert result is not None
    assert "name" in result
