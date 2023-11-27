from pydantic import Field, BaseModel

from location.citygeonames import CityGeonames


class LocationProjectBase(BaseModel):
    city: CityGeonames = Field(serialization_alias="city_id", validation_alias="city_id")
