from datetime import datetime

from pydantic import HttpUrl

from location.geopoint import GeoPoint
from location.schemas import LocationProjectBase


class EventOut(LocationProjectBase):
    title: str
    description: str
    image_urls: list[HttpUrl]
    start_at: datetime
    address: str
    location: GeoPoint