__all__ = ('DateOfBirth', 'Age')

from datetime import date
from typing import Annotated

from pydantic import PastDate, AfterValidator, BeforeValidator, PositiveInt
from pydantic_core import PydanticCustomError

from src.datehelpers import get_age
from src.profiles import config


def validate_birthday(value: date) -> date:
    today: date = date.today()
    year: int = value.year
    if not value.replace(year=year + config.MIN_AGE) <= today <= value.replace(year=year + config.MAX_AGE):
        raise PydanticCustomError("value_error", "Date of birth does not match the terms of use")
    return value


def validate_age(value: int | date) -> int:
    if isinstance(value, date):
        return get_age(value)
    return value


DateOfBirth = Annotated[PastDate, AfterValidator(validate_birthday)]
Age = Annotated[PositiveInt, BeforeValidator(validate_age)]
