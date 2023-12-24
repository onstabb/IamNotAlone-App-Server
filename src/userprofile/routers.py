from fastapi import APIRouter, status, Response

from userprofile import service
from userprofile.schemas import PrivateUserProfileIn
from users.dependencies import CurrentActiveUser
from users.schemas import UserPrivateOut


router = APIRouter()


@router.put(
    "",
    response_model=UserPrivateOut,
    responses={
        status.HTTP_200_OK: {"detail": "Profile updated"},
        status.HTTP_201_CREATED: {"detail": "Profile created"},
    },
)
def upsert_profile(profile_data: PrivateUserProfileIn, response: Response, user: CurrentActiveUser):
    if not user.profile:
        user = service.create_user_profile(user, profile_data)
        response.status_code = status.HTTP_201_CREATED
    else:
        user = service.update_user_profile(user, profile_data)
        response.status_code = status.HTTP_200_OK

    return user

