import base64
import json
import logging
import typing
from tempfile import TemporaryFile

from PIL import Image, UnidentifiedImageError
from pydantic import Json

from photos import config


log = logging.getLogger(__file__)


def filename_token_encode(extension: str, **additional_data: Json) -> str:
    """Encodes an JSON compatible information into filename"""
    data = json.dumps(additional_data, ensure_ascii=True)
    return f'{base64.b64encode(data.encode(encoding="ascii")).decode("ascii")}.{extension}'


def filename_token_decode(encoded_filename: str) -> dict:
    """Decodes base64 encoded filename with JSON data into dict"""
    data: dict = json.loads(base64.b64decode(encoded_filename.split(".")[0]))
    return data


def check_image_is_valid(file: typing.BinaryIO) -> bool:
    """
    Check if the provided binary file is a valid image.

    :param file: A binary file object to be checked.
    """

    try:
        image: Image = Image.open(file)
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


def image_compress(
        file: typing.BinaryIO, *,
        percent: int = config.FILE_IMAGE_COMPRESSION_PERCENT,
        max_pixel_size: int = config.FILE_IMAGE_MAX_PIXEL_SIZE,
    ) -> typing.BinaryIO:
    """
    Compresses an image read from the provided binary file and returns the compressed binary data.

    :param file: A binary file object representing the original image.
    :param percent: Compression percentage to be applied (default: config.FILE_IMAGE_COMPRESSION_PERCENT)
    :param max_pixel_size: Maximum pixel size for resizing the image (default: config.FILE_IMAGE_MAX_PIXEL_SIZE)

    :returns: A BinaryIO file object containing the compressed image data.
    """

    original_image: Image = Image.open(file)
    temp_file = TemporaryFile(suffix=f'.jpg')

    if max_pixel_size:
        width, height = original_image.size
        to_resize: bool = False
        width_ratio: float = 1.0
        height_ratio: float = 1.0

        if width > max_pixel_size:
            width_ratio = max_pixel_size / width
            to_resize = True

        if height > max_pixel_size:
            to_resize = True
            height_ratio = max_pixel_size / height

        if to_resize:
            reduce_factor = height_ratio if height_ratio < width_ratio else width_ratio
            original_image = original_image.resize((int(width * reduce_factor), int(height * reduce_factor)))

    quality: int = 100 - percent
    original_image.save(temp_file, format="jpeg", quality=quality, optimize=True)
    original_image.close()
    temp_file.seek(0)
    return temp_file
