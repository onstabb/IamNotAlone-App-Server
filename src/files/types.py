import os
from typing import Annotated

from pydantic import HttpUrl, AfterValidator

from src import config as global_config
from src.files import config, service


def validate(url: HttpUrl) -> HttpUrl:

    if url.host not in global_config.IMAGE_HOSTS:
        raise ValueError("forbidden host")

    path_split = os.path.split(url.path)

    if path_split[0] != config.IMAGE_FILES_PATH:
        raise ValueError("incorrect image files path")

    if not service.image_exists(url):
        raise ValueError(f'image does not exists')

    return url


ImageHttpUrl = Annotated[HttpUrl, AfterValidator(validate)]


if __name__ == '__main__':

    from pydantic import BaseModel

    class Image(BaseModel):
        url: ImageHttpUrl


    image = Image(url="http://127.0.0.1/static/images/d2d2f3d.jpg", )
    print(image.url)
