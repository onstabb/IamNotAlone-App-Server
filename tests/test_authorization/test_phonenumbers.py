import pytest

import pydantic

from src.authorization.mobilephonenumber import MobilePhoneNumber


MobilePhoneNumberAdapter = pydantic.TypeAdapter(MobilePhoneNumber)


@pytest.mark.parametrize(
    "number",
    [
        "+380961234567",
        "+380950123456",
        "+48888888888",
    ]
)
def test_correct_phone_number_format(number):
    mobile_phone_number = MobilePhoneNumberAdapter.validate_python(number)
    assert mobile_phone_number


@pytest.mark.parametrize(
    "number",
    [
        "331231",
        "380950123456",
        "symbol",
        "31-32-64",
        "710-050-313",
        pytest.param("+380950123456", marks=pytest.mark.xfail)
    ]
)
def test_incorrect_phone_number_format(number: str):
    try:
        MobilePhoneNumberAdapter.validate_python(number)
    except pydantic.ValidationError:
        return True
    else:
        raise AssertionError("Format must not be validated!")
