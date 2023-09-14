from typing import Annotated

from phonenumbers import (
    parse, NumberParseException, format_number, number_type, PhoneNumberFormat, is_valid_number, PhoneNumberType
)
from pydantic import AfterValidator


def validate_mobile_phone_number(value: str) -> str:
    try:
        phone_number = parse(value)
    except NumberParseException as exc:
        raise ValueError('value is not a valid phone number') from exc

    if not is_valid_number(phone_number):
        raise ValueError('value is not a valid phone number')

    if number_type(phone_number) != PhoneNumberType.MOBILE:
        raise ValueError('only mobile phone numbers allowed')

    return format_number(phone_number, PhoneNumberFormat.E164)


MobilePhoneNumber = Annotated[str, AfterValidator(validate_mobile_phone_number)]




