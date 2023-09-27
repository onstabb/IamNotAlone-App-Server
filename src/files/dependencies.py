from fastapi import Depends, UploadFile, HTTPException, status


from authorization.dependencies import get_unbanned_user
from authorization.models import User
from files import config, service, helpers


def upload_photo(photo: UploadFile, user: User = Depends(get_unbanned_user),) -> str:
    if photo.content_type not in config.SUPPORTED_IMAGE_MEDIA_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Expected media type: {config.SUPPORTED_IMAGE_MEDIA_TYPES}"
        )

    image_filename: str = service.save_image_and_create_token(upload_file=photo, subject=str(user.id))
    if not service.check_image_is_valid(image_filename):
        service.remove_image(image_filename)
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=f"Corrupted image file: {photo.filename}"
        )

    service.image_compress(image_filename)
    return f"{config.SERVER_STATIC_URL}/{image_filename}"

