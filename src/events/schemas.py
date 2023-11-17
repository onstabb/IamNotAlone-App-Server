from datetime import datetime

from pydantic import BaseModel, HttpUrl

from location.geopoint import GeoPoint


class EventLocationOut(BaseModel):
    city_id: int
    current: GeoPoint
    address: str


class EventOut(BaseModel):
    title: str
    description: str
    location: EventLocationOut
    image_urls: list[HttpUrl]
    start_at: datetime
