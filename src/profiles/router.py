from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse

from src.authorization.dependencies import get_unbanned_user
from src.authorization.models import User

from src.files import helpers as file_helpers
from src.profiles import service
from src.profiles.models import Profile
from src.profiles.dependencies import get_active_profile, get_active_profile_by_id
from src.profiles.schemas import PrivateProfileIn, PrivateProfileOut, PublicProfileOut


router: APIRouter = APIRouter(tags=['profiles'], prefix='/profiles')


@router.get("/me", response_model=PrivateProfileOut)
def get_my_profile(profile: Profile = Depends(get_active_profile)):
    return profile


@router.get("/{profile_id}", response_model=PublicProfileOut, dependencies=[Depends(get_active_profile)])
def get_profile(profile: Profile = Depends(get_active_profile_by_id)):
    return profile


@router.post("/me", response_model=PrivateProfileOut)
def edit_profile(profile_data: PrivateProfileIn, user: User = Depends(get_unbanned_user)):

    for photo_url in profile_data.photo_urls:

        file_token = file_helpers.get_image_token_from_url(photo_url)
        user_id, _created_at = file_helpers.file_token_decode(file_token)

        if user_id != user.id.__str__():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Images does not belongs to user")

    profile = service.create_or_update_profile(profile_data, user)
    return profile


@router.get("/{profile_id}/photos/{index}", dependencies=[Depends(get_active_profile)],)
def get_profile_photo(index: int, profile: Profile = Depends(get_active_profile_by_id)):

    try:
        photo_url = profile.photo_urls[index]
    except IndexError:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

    return RedirectResponse(photo_url, status_code=status.HTTP_302_FOUND)
