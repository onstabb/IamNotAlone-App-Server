__all__ = ('build_password', 'get_password_hash', 'verify_password', 'Password')

import string
import secrets

from passlib.context import CryptContext
from pydantic import constr

from src.authorization import config


ALPHABET = f'{string.ascii_letters}{string.digits}'
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


Password = constr(max_length=config.AUTH_GENERATED_PASSWORD_LENGTH)


def build_password(length: int = config.AUTH_GENERATED_PASSWORD_LENGTH) -> Password:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def get_password_hash(password: Password) -> str:
    return password_context.hash(password)


def verify_password(plain_password: str | bytes, hashed_password: str | bytes) -> bool:
    return password_context.verify(plain_password, hashed_password)
