from fastapi import APIRouter, UploadFile, Depends, HTTPException, status

from authorization.dependencies import get_unbanned_user
from authorization.models import User
from files.dependencies import upload_photo
from files.imageurl import ImageUrl
from profiles import config as database_config

router = APIRouter(tags=['Files'], prefix="/files")


upload_photo_responses = {415: {"error": "Unsupported media type"}, 406: {"error": "Corrupted image file"}}
upload_photos_responses = upload_photo_responses.copy()
upload_photos_responses[413] = {"error": "Too many files"}


@router.put(
    "/photo",
    responses=upload_photo_responses,
    response_model=ImageUrl,
    status_code=status.HTTP_201_CREATED
)
def upload_one_photo(image_url: str = Depends(upload_photo)):
    return image_url


@router.put(
    "/photos",
    responses=upload_photos_responses,
    response_model=list[ImageUrl],
    status_code=status.HTTP_201_CREATED
)
def upload_photos(photos: list[UploadFile], user: User = Depends(get_unbanned_user)):

    if len(photos) > database_config.MAX_PROFILE_PHOTOS:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"too many files >{database_config.MAX_PROFILE_PHOTOS}"
        )

    return [upload_photo(photo, user) for photo in photos]
