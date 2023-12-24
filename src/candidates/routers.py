from fastapi import APIRouter

from candidates import service
from users.dependencies import CurrentActiveCompletedUser
from users.schemas import UserPublicOut


router = APIRouter()


@router.get("", response_model=list[UserPublicOut])
def get_candidates(current_user: CurrentActiveCompletedUser):
    return service.get_candidates_by_user(current_user, limit=1)
