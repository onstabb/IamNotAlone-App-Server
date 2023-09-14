import logging
import os
import shutil
import typing
from pathlib import Path

from PIL import Image, UnidentifiedImageError
from fastapi import UploadFile

from files import config
from files.helpers import get_image_filename_from_url, file_token_create


if typing.TYPE_CHECKING:
    from files.imageurl import ImageUrl


log = logging.getLogger(__file__)


def check_image_is_valid(image_filename: str) -> bool:
    image_path: str = get_image_file_dir(image_filename)
    try:
        image: Image = Image.open(image_path)
    except UnidentifiedImageError:
        return False
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
    image_filename: str = get_image_filename_from_url(image_url)
    return image_exists_from_filename(image_filename)


def image_exists_from_filename(image_filename: str) -> bool:
    return os.path.exists(get_image_file_dir(image_filename))


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


def save_upload_file(file: typing.BinaryIO, destination: Path) -> None:
    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(file, buffer)
    finally:
        file.close()


def save_image_and_create_token(upload_file: UploadFile, subject: str) -> str:
    image_url = file_token_create(str(subject))
    filename = f'{image_url}.{upload_file.filename.split(".")[-1]}'
    destination = Path(os.path.join(config.IMAGE_FILES_LOCAL_PATH, filename))
    save_upload_file(upload_file.file, destination)
    return filename


def remove_image(image_filename: str) -> None:
    os.remove(get_image_file_dir(image_filename))


def remove_image_if_exists(image_filename: str) -> None:
    if not image_exists_from_filename(image_filename):
        return
    remove_image(image_filename)
