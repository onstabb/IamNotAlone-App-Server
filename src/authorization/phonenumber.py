from typing import Annotated

import phonenumbers
from pydantic import AfterValidator


def validate_mobile_phone_number(value: str) -> str:
    try:
        phone_number = phonenumbers.parse(value)
    except phonenumbers.NumberParseException as exc:
        raise ValueError('value is not a valid phone number') from exc

    if not phonenumbers.is_valid_number(phone_number):
        raise ValueError('value is not a valid phone number')

    if phonenumbers.number_type(phone_number) != phonenumbers.PhoneNumberType.MOBILE:
        raise ValueError('only mobile phone numbers allowed')

    return phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)


MobilePhoneNumber = Annotated[str, AfterValidator(validate_mobile_phone_number)]
