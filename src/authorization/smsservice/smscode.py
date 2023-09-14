__all__ = ("SmsCode", "generate_code")

import string
from secrets import choice

from pydantic import constr

from src.authorization import config


SmsCode = constr(max_length=config.SMS_GENERATED_CODE_LENGTH, min_length=config.SMS_GENERATED_CODE_LENGTH)


def generate_code(length: int = config.SMS_GENERATED_CODE_LENGTH) -> 'SmsCode':
    return "".join(choice(string.digits) for _ in range(length))
