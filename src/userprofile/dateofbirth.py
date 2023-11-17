__all__ = ('DateOfBirth', 'Age')

from datetime import date, datetime
from typing import Annotated

from pydantic import PastDate, AfterValidator, BeforeValidator, PositiveInt

from userprofile import config


def validate_date_of_birth(value: date) -> date:
    today: date = date.today()
    year: int = value.year
    if not value.replace(year=year + config.MIN_AGE) <= today <= value.replace(year=year + config.MAX_AGE):
        raise ValueError("Date of birth does not match the terms of use")
    return value


def validate_age(value: int | date) -> int:
    if isinstance(value, date) or isinstance(value, datetime):
        delta = date.today() - date(value.year, value.month, value.day)
        return delta.days
    return value


DateOfBirth = Annotated[PastDate, AfterValidator(validate_date_of_birth)]
Age = Annotated[PositiveInt, BeforeValidator(validate_age)]