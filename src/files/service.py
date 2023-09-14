import logging
import os
import shutil
import typing
from pathlib import Path

from PIL import Image
from fastapi import UploadFile

from src.files import config
from src.files.helpers import get_image_token_from_url


if typing.TYPE_CHECKING:
    from src.files.imageurl import ImageUrl


log = logging.getLogger(__file__)


def check_image_is_valid(image_filename: str) -> bool:
    image_path: str = get_image_file_dir(image_filename)
    image: Image = Image.open(image_path)

    try:
        image.verify()
        return True
    except Exception as e:
        log.error(e)
    finally:
        image.close()
    return False


def get_image_file_dir(image_filename: str) -> str:
    return os.path.join(config.IMAGE_FILES_LOCAL_PATH, image_filename)


def image_exists(image_url: typing.Union[str, 'ImageUrl']) -> bool:
    file_token: str = get_image_token_from_url(image_url)
    return os.path.exists(get_image_file_dir(file_token))


def image_compress(image_filename: str) -> None:
    image_path: str = get_image_file_dir(image_filename)
    original_image: Image = Image.open(image_path)

    width, height = original_image.size
    resize: bool = False
    width_ratio: float = 1.0
    height_ratio: float = 1.0

    if width > config.FILE_IMAGE_MAX_PIXEL_SIZE:
        width_ratio = config.FILE_IMAGE_MAX_PIXEL_SIZE / width
        resize = True
    if height > config.FILE_IMAGE_MAX_PIXEL_SIZE:
        resize = True
        height_ratio = config.FILE_IMAGE_MAX_PIXEL_SIZE / height

    if resize:
        if height_ratio < width_ratio:
            reduce_factor = height_ratio
        else:
            reduce_factor = width_ratio

        original_image = original_image.resize((int(width * reduce_factor), int(height * reduce_factor)))

    quality: int = 100 - config.FILE_IMAGE_COMPRESSION_PERCENT

    original_image.save(image_path, original_image.format, quality=quality, optimize=True)
    original_image.close()


def save_upload_file(upload_file: UploadFile, destination: Path) -> None:
    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()


def save_image(upload_file: UploadFile, token: str) -> str:
    image_url = token
    filename = f'{image_url}.{upload_file.filename.split(".")[-1]}'
    destination = Path(os.path.join(config.IMAGE_FILES_LOCAL_PATH, filename))
    save_upload_file(upload_file, destination)
    return filename
