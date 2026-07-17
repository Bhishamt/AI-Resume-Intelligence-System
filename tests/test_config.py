from src.utils.config import Config


def test_config_has_required_attributes():
    assert hasattr(Config, "GEMINI_API_KEY")
    assert hasattr(Config, "GROQ_API_KEY")
    assert hasattr(Config, "APP_MODE")
    assert hasattr(Config, "OUTPUT_DIR")
    assert hasattr(Config, "ATS_KEYWORDS_PATH")


def test_config_validate_config_returns_list():
    result = Config.validate_config()
    assert isinstance(result, list)


def test_config_master_resume_path():
    path = Config.MASTER_RESUME_PATH
    assert path is not None
    assert isinstance(path, str)
