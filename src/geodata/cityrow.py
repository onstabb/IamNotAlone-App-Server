from pydantic import BaseModel, ConfigDict

from geodata.geopoint import GeoPointType


class CityRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    geonameid: int
    name: str
    coordinates: GeoPointType
    administrative_unit_name: str
    country_name: str
    country_code: str
