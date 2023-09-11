import string
from secrets import choice

from src.authorization.types import SmsCode


def generate_code(n: int) -> SmsCode:
    return "".join(choice(string.digits) for _ in range(n))
