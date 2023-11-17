from fastapi import APIRouter


from users.dependencies import (
    CurrentActiveUser,
    TargetActiveCompletedUser
)
from users.schemas import UserPrivateOut, UserPublicOut


router: APIRouter = APIRouter()


@router.get("/me", response_model=UserPrivateOut)
def get_me(user: CurrentActiveUser):
    return user


@router.get("/{user_id}", response_model=UserPublicOut)
def get_user(user: TargetActiveCompletedUser):
    return user
