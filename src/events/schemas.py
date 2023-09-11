from pydantic import BaseModel, HttpUrl, Field, AwareDatetime

from src.geodata.basetypes import GeoPoint
from src.geodata.types import CityGeonames


class EventOut(BaseModel):
    title: str
    description: str
    address: str
    city: CityGeonames = Field(serialization_alias="city_id")
    coordinates: GeoPoint
    image_urls: list[HttpUrl]
    start_at: AwareDatetime
