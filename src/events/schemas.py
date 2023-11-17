from pydantic import BaseModel, HttpUrl, AwareDatetime

from location.geopoint import GeoPoint


class EventLocationOut(BaseModel):
    city_id: int
    city: GeoPoint
    current: GeoPoint
    address: str


class EventOut(BaseModel):
    title: str
    description: str
    location: EventLocationOut
    image_urls: list[HttpUrl]
    start_at: AwareDatetime
