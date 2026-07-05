from src.utils.validators import validate_email

def test_validate_email():
    assert validate_email('test@example.com')