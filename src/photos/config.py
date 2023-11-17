import os
from pathlib import Path

import config as global_config


IMAGE_FILES_LOCAL_PATH: Path = global_config.STATIC_PATH / "images"
if not IMAGE_FILES_LOCAL_PATH.exists():
    IMAGE_FILES_LOCAL_PATH.mkdir()

SERVER_STATIC_IMAGES_URL = f'{global_config.SERVER_URL}/static/images'
SUPPORTED_IMAGE_FORMATS = ('jpeg', 'jpg', 'bmp', 'png')
SUPPORTED_IMAGE_MEDIA_TYPES = tuple(f'image/{img_format}' for img_format in SUPPORTED_IMAGE_FORMATS)
FILE_TOKEN_LENGTH = 24
FILE_IMAGE_COMPRESSION_PERCENT: int = 50
FILE_IMAGE_MAX_SIZE = 5 * 1024 * 1024
FILE_IMAGE_MAX_PIXEL_SIZE = 600

MAX_PROFILE_PHOTOS = 3


S3_API_ENDPOINT = os.getenv("S3_API_ENDPOINT", "https://s3.filebase.com")
S3_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY_ID")
S3_SECRET_ACCESS_KEY_ID = os.getenv("S3_SECRET_ACCESS_KEY_ID")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME","iamnotalone")
S3_IPFS_URL = os.getenv("S3_IPFS_URL", "https://ipfs.filebase.io/ipfs")
