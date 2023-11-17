__all__ = (
    'get_token_expiration_from_now', 'create_access_token', 'JWTBearer',
    'generate_password', 'hash_password', 'verify_password'
)

from datetime import datetime, timedelta

import passlib.context
import passlib.pwd
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt, JWTError
from pytz import utc

import config
from datehelpers import get_aware_datetime_now


password_context = passlib.context.CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(subject: str, expires_at: datetime) -> str:
    to_encode = {"sub": str(subject), "exp": expires_at}
    encoded = jwt.encode(to_encode, key=config.AUTH_SECRET_KEY, algorithm=config.AUTH_ALGORYTHM)
    return encoded


def get_subject_from_access_token(token: str) -> str:
    try:
        payload: dict = jwt.decode(token, key=config.AUTH_SECRET_KEY, algorithms=[config.AUTH_ALGORYTHM])
    except JWTError:
        return ""

    expires_at = datetime.fromtimestamp(payload['exp'], utc)
    if get_aware_datetime_now() > expires_at:
        return ""

    return payload.get("sub", "")


def get_token_expiration_from_now() -> datetime:
    return get_aware_datetime_now() + timedelta(days=config.ACCESS_TOKEN_EXPIRE_DAYS)


class _JWTBearer(HTTPBearer):

    def __init__(self, scheme_name: str, auto_error: bool = False):
        super(_JWTBearer, self).__init__(scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> str:
        authorization = request.headers.get("Authorization")
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not scheme or not credentials or not authorization:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        if scheme.lower() != "bearer":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid `{scheme}` scheme")

        subject = get_subject_from_access_token(credentials)
        if not subject:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

        return subject


JWTBearer = _JWTBearer(scheme_name="Bearer JWT")


def generate_password(length: int = 8) -> str:
    return passlib.pwd.genword(length=length)


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(plain_password: str | bytes, hashed_password: str | bytes) -> bool:
    return password_context.verify(plain_password, hashed_password)
