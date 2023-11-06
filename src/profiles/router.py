from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, Path
from fastapi.responses import RedirectResponse, Response


from authorization.dependencies import get_unbanned_user
from authorization.models import User
from profiles import config
from profiles import service
from profiles.dependencies import (
    CurrentOrActiveTargetProfile,
    CurrentProfileByToken,
    CurrentActiveProfileByToken,
    ActiveTargetProfileById,
    CurrentActiveProfileByToken
)
from files.dependencies import upload_photo
from profiles.schemas import PrivateProfileIn, PrivateProfileOut, PublicProfileOut


router: APIRouter = APIRouter()


@router.get("/my", response_model=PrivateProfileOut)
def get_my_profile(profile: CurrentActiveProfileByToken):
    return profile


@router.get("/{profile_id}", response_model=PublicProfileOut)
def get_profile(profile: ActiveTargetProfileById):
    return profile


@router.get("/my/candidates", response_model=list[PublicProfileOut])
def get_candidates(current_profile: CurrentActiveProfileByToken):
    return service.get_candidates(current_profile)


@router.post(
    "",
    response_model=PrivateProfileOut,
    responses={
        status.HTTP_200_OK: {"detail": "Profile updated"}, status.HTTP_201_CREATED: {"detail": "Profile created"},
    },
)
def upsert_profile(profile_data: PrivateProfileIn, response: Response, user: User = Depends(get_unbanned_user)):
    if not user.profile:
        profile = service.create_profile(profile_data, user)
        response.status_code = status.HTTP_201_CREATED
    else:
        profile = service.update_profile(profile_data, user.profile)
        response.status_code = status.HTTP_200_OK
    return profile


@router.get("/{profile_id}/photos/{index}", response_class=RedirectResponse)
def get_profile_photo(index: int, profile: CurrentOrActiveTargetProfile):
    try:
        photo_url = profile.photo_urls[index]
    except IndexError:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    return RedirectResponse(photo_url, status_code=status.HTTP_302_FOUND)


@router.post("/my/photos", response_model=PrivateProfileOut, status_code=status.HTTP_201_CREATED)
def upload_profile_photos(photos: list[UploadFile], current_profile: CurrentProfileByToken):

    if len(current_profile.photo_urls)+1 > config.MAX_PROFILE_PHOTOS:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="")
    if len(photos) > config.MAX_PROFILE_PHOTOS:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"too many files >{config.MAX_PROFILE_PHOTOS}"
        )
    current_profile.photo_urls = [upload_photo(photo, current_profile) for photo in photos]
    current_profile.save()
    return current_profile


@router.put("/my/photos/{list_index}", response_model=PrivateProfileOut)
def update_profile_photo(
        photo: UploadFile,
        current_profile: CurrentProfileByToken,
        list_index: int = Path(lt=config.MAX_PROFILE_PHOTOS, ge=0)
):

    if list_index > len(current_profile.photo_urls):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

    image_url = upload_photo(photo, current_profile)

    if list_index == len(current_profile.photo_urls):
        current_profile.photo_urls.append(image_url)

    if list_index < len(current_profile.photo_urls):
        current_profile.photo_urls[list_index] = image_url

    current_profile.save()
    return current_profile

