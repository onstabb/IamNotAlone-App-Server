from fastapi import APIRouter

from candidates import service
from users.dependencies import CurrentActiveCompletedUser
from users.schemas import UserPublicOut


router = APIRouter()


@router.get("", response_model=list[UserPublicOut])
def get_candidates(current_profile: CurrentActiveCompletedUser):
    return service.get_candidates_for_user(current_profile)
