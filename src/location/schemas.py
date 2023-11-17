from pydantic import BaseModel, Field

from location.citygeonames import CityGeonames


class LocationProjectBase(BaseModel):
    city: CityGeonames = Field(serialization_alias="city_id", validation_alias="city_id")
