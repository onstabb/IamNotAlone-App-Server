from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, Response

from authorization.dependencies import get_unbanned_user
from authorization.models import User

from files import helpers as file_helpers
from files import service as file_service
from profiles import service
from profiles.models import Profile
from profiles.dependencies import get_active_profile, get_active_profile_by_id
from profiles.schemas import PrivateProfileIn, PrivateProfileOut, PublicProfileOut


router: APIRouter = APIRouter(tags=['Profiles'], prefix='/profiles')


@router.get("/me", response_model=PrivateProfileOut)
def get_my_profile(profile: Profile = Depends(get_active_profile)):
    return profile


@router.get("/{profile_id}", response_model=PublicProfileOut, dependencies=[Depends(get_active_profile)])
def get_profile(profile: Profile = Depends(get_active_profile_by_id)):
    return profile


@router.post(
    "/me",
    response_model=PrivateProfileOut,
    status_code=status.HTTP_200_OK,
    responses={200: {"detail": "Profile updated"}, 201: {"detail": "Profile created"}},
)
def edit_profile(profile_data: PrivateProfileIn, response: Response, user: User = Depends(get_unbanned_user)):

    for photo_url in profile_data.photo_urls:

        file_token = file_helpers.get_image_filename_from_url(photo_url)
        user_id, _created_at = file_helpers.file_token_decode(file_token)

        if not file_service.image_exists(photo_url):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image {file_token} could not be found"
            )

        if user_id != str(user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You don't have permission to access {file_token} image"
            )

    response.status_code = status.HTTP_201_CREATED if user.profile is None else status.HTTP_200_OK
    profile = service.create_or_update_profile(profile_data, user)
    return profile


@router.get("/{profile_id}/photos/{index}", dependencies=[Depends(get_active_profile)],)
def get_profile_photo(index: int, profile: Profile = Depends(get_active_profile_by_id)):

    try:
        photo_url = profile.photo_urls[index]
    except IndexError:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

    return RedirectResponse(photo_url, status_code=status.HTTP_302_FOUND)
