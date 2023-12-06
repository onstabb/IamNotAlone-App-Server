__all__ = ('BirthDate', 'Age')

from datetime import date, datetime, timedelta
from typing import Annotated

from pydantic import PastDate, AfterValidator, BeforeValidator, PositiveInt

from userprofile import config


def validate_birthdate(value: date) -> date:
    today: date = date.today()
    year: int = value.year
    if not value.replace(year=year + config.MIN_AGE) <= today <= value.replace(year=year + config.MAX_AGE):
        raise ValueError("Date of birth does not match the terms of use")
    return value


def validate_age(value: int | date | datetime) -> int:
    if isinstance(value, date) or isinstance(value, datetime):
        birthdate = date(value.year, value.month, value.day)
        age = (date.today() - birthdate) // timedelta(days=365.2425)
        return age

    return value


BirthDate = Annotated[PastDate, AfterValidator(validate_birthdate)]
Age = Annotated[PositiveInt, BeforeValidator(validate_age)]
