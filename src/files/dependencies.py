import os

from fastapi import Depends, UploadFile, HTTPException, status


from src.authorization.dependencies import get_unbanned_user
from src.authorization.models import User
from src.files import config, service, helpers


def upload_photo(photo: UploadFile, user: User = Depends(get_unbanned_user),) -> str:
    if photo.content_type not in config.SUPPORTED_IMAGE_MEDIA_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Expected media type: {config.SUPPORTED_IMAGE_MEDIA_TYPES}"
        )

    image_ref: str = service.save_image(upload_file=photo, token=helpers.file_token_create(subject=user.id.__str__()))
    if not service.check_image_is_valid(image_ref):
        os.remove(service.get_image_file_dir(image_ref))
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=f"Corrupted image file: {photo.filename}"
        )

    service.image_compress(image_ref)
    return f"{config.SERVER_STATIC_URL}/{image_ref}"

