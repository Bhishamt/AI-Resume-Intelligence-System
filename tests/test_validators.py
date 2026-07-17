import pytest
from src.utils.validators import validate_email


def test_valid_email():
    assert validate_email("test@example.com")
    assert validate_email("user.name+tag@domain.co.uk")
    assert validate_email("valid@subdomain.example.org")


def test_invalid_email():
    assert not validate_email("")
    assert not validate_email("not-an-email")
    assert not validate_email("@missing-user.com")
    assert not validate_email("user@")
    assert not validate_email("user@.com")
    assert not validate_email(None)


def test_edge_cases():
    assert not validate_email("a@b.c")
    assert not validate_email("plainaddress")
