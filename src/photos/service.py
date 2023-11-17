from photos.bucket import FileBucket, S3Bucket
from users.models import User


_bucket: FileBucket = S3Bucket()


def get_bucket() -> FileBucket:
    global _bucket
    return _bucket


def set_bucket(client: FileBucket) -> FileBucket:
    global _bucket
    _bucket = client
    return client


def upsert_photo_url(new_url: str, user: User, index: int) -> User:
    if index == len(user.photo_urls):
        user.photo_urls.append(new_url)
    else:
        user.photo_urls[index] = new_url

    user.save()
    return user
