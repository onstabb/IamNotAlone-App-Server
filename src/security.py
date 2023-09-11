__all__ = ('get_token_expiration_from_now', 'create_access_token', 'JWTBearer', 'WebSocketJWTBearer')

from datetime import datetime, timedelta
from typing import NoReturn

from fastapi import Request, HTTPException, WebSocketException, WebSocket, status
from fastapi.security import HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt, JWTError
from pytz import utc

from src import config
from src.dateutil import get_aware_datetime_now


def create_access_token(subject: str, expires_at: datetime) -> str:
    to_encode = {"sub": str(subject), "exp": expires_at}
    return jwt.encode(to_encode, key=config.AUTH_SECRET_KEY, algorithm=config.AUTH_ALGORYTHM)


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


def _raise_auth_error(connection: Request | WebSocket, detail: str) -> NoReturn:
    if isinstance(connection, Request):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
    else:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason=detail)

def _validate(connection: Request | WebSocket) -> str:

    authorization = connection.headers.get("Authorization")
    scheme, credentials = get_authorization_scheme_param(authorization)
    if not scheme or not credentials or not authorization:
        _raise_auth_error(connection, "Not authenticated")

    if scheme.lower() != "bearer":
        _raise_auth_error(connection, f"Invalid `{scheme}` scheme")

    subject = get_subject_from_access_token(credentials)
    if not subject:
        _raise_auth_error(connection, "Invalid or expired token")

    return subject


class _JWTBearer(HTTPBearer):

    def __init__(self, scheme_name: str, auto_error: bool = False):
        super(_JWTBearer, self).__init__(scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> str:
        return _validate(request)


class _WebSocketJWTBearer:

    def __call__(self, websocket: WebSocket, ) -> str:
        return _validate(websocket)


JWTBearer = _JWTBearer(scheme_name="Bearer JWT")
WebSocketJWTBearer = _WebSocketJWTBearer()
