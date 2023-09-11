import base64
import json
import os
import secrets
import typing
from datetime import datetime
from urllib.parse import urlparse

from pydantic_core import Url
from pytz import utc

from files.types import ImageHttpUrl


def file_token_generate(n_bytes: int = 16) -> str:
    return secrets.token_urlsafe(n_bytes)


FileTokenSubject = str | int


def file_token_create(subject: FileTokenSubject) -> str:

    data = json.dumps({"subject": subject, "created_at": datetime.now(tz=utc).isoformat()}, ensure_ascii=True)
    return base64.b64encode(data.encode(encoding="ascii")).decode("ascii")


def file_token_decode(token: str) -> tuple[FileTokenSubject, datetime]:
    data: dict = json.loads(base64.b64decode(token))
    data['created_at'] = datetime.fromisoformat(data['created_at'])
    return data['subject'], data['created_at']


def get_image_token_from_url(image_url: typing.Union['ImageHttpUrl', str]) -> str:

    if isinstance(image_url, Url):
        data_path = image_url.path
    else:
        data_path = urlparse(image_url).path

    return os.path.split(data_path)[-1]
