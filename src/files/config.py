import os

from src import config as global_config

IMAGE_FILES_STATIC_PATH: str = "/static/images"
IMAGE_FILES_LOCAL_PATH: str = os.path.join(global_config.STATIC_PATH, "images")

if not os.path.exists(IMAGE_FILES_LOCAL_PATH):
    os.makedirs(IMAGE_FILES_LOCAL_PATH)

SERVER_STATIC_URL: str = f'{global_config.SERVER_URL}{IMAGE_FILES_STATIC_PATH}'
SUPPORTED_IMAGE_FORMATS: tuple[str, ...] = ('jpeg', 'jpg', 'bmp', 'png')
SUPPORTED_IMAGE_MEDIA_TYPES: tuple[str, ...] = tuple(f'image/{img_format}' for img_format in SUPPORTED_IMAGE_FORMATS)
FILE_TOKEN_LENGTH: int = 24
FILE_IMAGE_COMPRESSION_PERCENT: int = 50
FILE_IMAGE_MAX_SIZE: int = 5 * 1024 * 1024
FILE_IMAGE_MAX_PIXEL_SIZE: int = 600
