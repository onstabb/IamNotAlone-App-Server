import shutil
import typing


from photos import config
from photos.bucket.base import BaseBucket


class LocalBucket(BaseBucket):

    def upload(self, file: typing.BinaryIO, filename: str, **kwargs) -> str:
        destination = config.BUCKET_FILES_LOCAL_PATH / filename
        try:
            with destination.open("wb") as buffer:
                shutil.copyfileobj(file, buffer)
        finally:
            file.close()

        return f"{config.SERVER_STATIC_IMAGES_URL}/{filename}"
