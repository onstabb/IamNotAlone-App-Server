from fastapi import APIRouter, UploadFile, Depends, HTTPException, status

from src.authorization.dependencies import get_unbanned_user
from profiles import config as database_config
from authorization.models import User

from src.files.dependencies import upload_photo
from src.files.types import ImageHttpUrl

router = APIRouter(tags=['files'], prefix="/files")


upload_photo_responses = {415: {"error": "Unsupported media type"}, 406: {"error": "Corrupted image file"}}
upload_photos_responses = upload_photo_responses.copy()
upload_photos_responses[413] = {"error": "Too many files"}


@router.post("/photo", responses=upload_photo_responses, response_model=ImageHttpUrl)
def upload_one_photo(image_url: str = Depends(upload_photo)):
    return image_url


@router.post("/photos", responses=upload_photos_responses, response_model=list[ImageHttpUrl])
def upload_photos(photos: list[UploadFile], user: User = Depends(get_unbanned_user)):

    if len(photos) > database_config.MAX_PROFILE_PHOTOS:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"too many files >{database_config.MAX_PROFILE_PHOTOS}"
        )

    return [upload_photo(photo, user) for photo in photos]
