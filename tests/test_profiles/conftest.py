import os.path

from conftest import DATA_DIR


IMAGE_DIR = os.path.join(DATA_DIR, "images")


def get_image_path(image_file: str) -> str:
    return os.path.join(IMAGE_DIR, image_file)