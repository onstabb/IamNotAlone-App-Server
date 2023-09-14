from fastapi import HTTPException, status, Depends


from authorization.service import get_user_by_id
from authorization.models import User
from security import JWTBearer




def get_user_by_token(subject: str = Depends(JWTBearer)) -> User:
    user: User | None = get_user_by_id(user_id=subject)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user


def get_unbanned_user(user: User = Depends(get_user_by_token)) -> User:
    if user.banned:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User has been banned")
    return user
