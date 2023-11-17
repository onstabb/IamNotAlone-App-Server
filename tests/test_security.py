from datetime import datetime

import pytest


import security
from datehelpers import get_aware_datetime_now


@pytest.mark.parametrize(
    "subject,expires_at",
    [
        ("2jfj221d", get_aware_datetime_now(delta_days=1)),
    ]
)
def test_correct_token_encoding(subject: str, expires_at: datetime):
    token = security.create_access_token(subject, expires_at)
    assert security.get_subject_from_access_token(token) == subject


@pytest.mark.parametrize(
    "subject,expires_at",
    [
        ("2jfj221d", get_aware_datetime_now(delta_days=-1)),
    ]
)
def test_expired_token_encoding(subject: str, expires_at: datetime):
    token = security.create_access_token(subject, expires_at)
    assert security.get_subject_from_access_token(token) == ""


@pytest.mark.parametrize(
    "invalid_token",
    [
        "...@definitely_incorrect@...",
    ]
)
def test_invalid_token(invalid_token: str):
    assert security.get_subject_from_access_token(invalid_token) == ""


def test_passwords():
    password = "12345"
    hashed_password = security.hash_password(password)

    assert security.verify_password(password, hashed_password)
