from datetime import datetime, timedelta

import pytest
import pytz

from src import security


def get_datetime_from_now(delta_days: int) -> datetime:
    return datetime.now(pytz.utc) + timedelta(days=delta_days)


@pytest.mark.parametrize(
    "subject,expires_at",
    [
        ("2jfj221d", get_datetime_from_now(10)),
        ("user_exp", get_datetime_from_now(16)),
        pytest.param("subject1", get_datetime_from_now(-3), marks=pytest.mark.xfail),
        pytest.param("user_exp", get_datetime_from_now(-15), marks=pytest.mark.xfail)
    ]
)
def test_correct_token_encoding(subject: str, expires_at: datetime):
    token = security.create_access_token(subject, expires_at)
    assert security.get_subject_from_access_token(token) == subject


@pytest.mark.parametrize(
    "subject,expires_at",
    [
        ("2jfj221d", get_datetime_from_now(-10)),
        ("user_exp", get_datetime_from_now(-16)),
    ]
)
def test_expired_token_encoding(subject: str, expires_at: datetime):
    token = security.create_access_token(subject, expires_at)
    assert security.get_subject_from_access_token(token) == ""


@pytest.mark.parametrize(
    "invalid_token",
    [
        "d21kgm000ma2-=",
        "definitely_incorrect",
        "%"
    ]
)
def test_invalid_token(invalid_token: str):
    assert security.get_subject_from_access_token(invalid_token) == ""
