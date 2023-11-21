from fastapi import APIRouter

from likes import service
from users.dependencies import CurrentActiveCompletedUser
from users.schemas import UserPublicOut


router = APIRouter()


@router.get("", response_model=list[UserPublicOut])
def get_who_liked(current_user: CurrentActiveCompletedUser):
    return [contact.initiator for contact in service.get_likes_for_user(current_user)]

