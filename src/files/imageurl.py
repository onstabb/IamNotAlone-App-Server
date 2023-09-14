import os
from typing import Annotated

from pydantic import HttpUrl, AfterValidator

from src import config as global_config
from files import config


def validate(url: HttpUrl) -> HttpUrl:

    if url.host not in global_config.IMAGE_HOSTS:
        raise ValueError("forbidden host")

    path_split = os.path.split(url.path)

    if path_split[0] != config.IMAGE_FILES_STATIC_PATH:
        raise ValueError("incorrect image files path")

    return url


ImageUrl = Annotated[HttpUrl, AfterValidator(validate)]
