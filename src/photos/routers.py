from fastapi import UploadFile, status, APIRouter, HTTPException, Path


from photos import config, helpers, service
from users.dependencies import CurrentActiveUser
from users.schemas import UserPrivateOut


router: APIRouter = APIRouter()


@router.put("/{list_index}", response_model=UserPrivateOut)
def update_profile_photo(
        photo: UploadFile,
        current_user: CurrentActiveUser,
        list_index: int = Path(lt=config.MAX_PROFILE_PHOTOS, ge=0,)

):
    if list_index > len(current_user.photo_urls):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid index")

    if photo.content_type not in config.SUPPORTED_IMAGE_MEDIA_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Expected media type: {config.SUPPORTED_IMAGE_MEDIA_TYPES}"
        )

    if photo.size > config.FILE_IMAGE_MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File is too large > {config.FILE_IMAGE_MAX_SIZE / 1024 / 1024} Mb"
        )

    if not helpers.check_image_is_valid(photo.file):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=f"Corrupted image file: {photo.filename}"
        )

    compressed_image = helpers.image_compress(photo.file)
    image_url = service.get_bucket().upload(
        compressed_image,
        filename=helpers.filename_token_encode(photo.filename, user_id=str(current_user.id), index=list_index),
        ContentType=photo.content_type
    )

    service.upsert_photo_url(image_url, user=current_user, index=list_index)
    return current_user
