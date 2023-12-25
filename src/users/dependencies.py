from typing import Annotated

from fastapi import Depends, HTTPException, status

from datehelpers import get_aware_datetime_now
from models import PydanticObjectId

from security import JWTBearer
from users import service
from users.models import User



def get_current_user_by_token(subject: str = Depends(JWTBearer),) -> User:
    user: User | None = service.get_user_by_id(user_id=subject)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    if user.banned:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is banned")

    return user


def get_current_active_user(user: User = Depends(get_current_user_by_token)) -> User:
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Activation is required")

    user.last_online = get_aware_datetime_now()
    return user


def get_current_active_completed_user(user: User = Depends(get_current_active_user)) -> User:
    if not user.profile or not user.photo_urls:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Completed profile is required")
    return user


# Target, Completed and Active
def get_active_completed_user(user_id: PydanticObjectId) -> User:
    user = service.get_active_completed_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id `{user_id}` not found or inactive"
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user_by_token)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
CurrentActiveCompletedUser = Annotated[User, Depends(get_current_active_completed_user)]
TargetActiveCompletedUser = Annotated[User, Depends(get_active_completed_user)]
