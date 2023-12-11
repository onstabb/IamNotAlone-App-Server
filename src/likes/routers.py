from fastapi import APIRouter

from contacts.schemas import ContactBaseOut
from likes import service
from users.dependencies import CurrentActiveCompletedUser


router = APIRouter()


@router.get("", response_model=list[ContactBaseOut])
def get_who_liked(current_user: CurrentActiveCompletedUser):
    return service.get_likes_for_user(current_user)
