__all__ = ('build_password', 'get_password_hash', 'verify_password')

import string
import secrets
from typing import AnyStr

from passlib.context import CryptContext

ALPHABET: str = f'{string.ascii_letters}{string.digits}'
password_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")


def build_password(length: int = 8) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def get_password_hash(password: str) -> str:
    return password_context.hash(password)


def verify_password(plain_password: AnyStr, hashed_password: AnyStr) -> bool:
    return password_context.verify(plain_password, hashed_password)
