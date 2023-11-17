import base64
import json
import logging
import os
import typing
from tempfile import TemporaryFile
from urllib.parse import urlparse

from PIL import Image, UnidentifiedImageError
from pydantic import HttpUrl, Json
from pydantic_core import Url


from photos import config


log = logging.getLogger(__file__)


def filename_token_encode(filename: str, **additional_data: Json) -> str:
    additional_data.update(filename=filename)
    data = json.dumps(additional_data, ensure_ascii=True)
    extension = filename.split(".")[-1]
    return f'{base64.b64encode(data.encode(encoding="ascii")).decode("ascii")}.{extension}'


def filename_token_decode(encoded_filename: str) -> Json:
    data: dict = json.loads(base64.b64decode(encoded_filename.split(".")[0]))
    return data


def get_image_filename_from_url(image_url: typing.Union[HttpUrl, str]) -> str:
    if isinstance(image_url, Url):
        data_path = image_url.path
    else:
        data_path = urlparse(image_url).path

    return os.path.split(data_path)[-1]


def check_image_is_valid(file: typing.BinaryIO) -> bool:
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
    ) -> TemporaryFile:

    """ Creates a temporary file with compressed image """

    original_image: Image = Image.open(file)
    temp_file = TemporaryFile(suffix=f'.{original_image.format.lower()}')

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
    original_image.save(temp_file, original_image.format, quality=quality, optimize=True)
    original_image.close()
    temp_file.seek(0)
    return temp_file
