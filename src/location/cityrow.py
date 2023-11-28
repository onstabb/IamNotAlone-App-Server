from pydantic import BaseModel, ConfigDict

from location.geopoint import GeoPoint


class CityRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    geonameid: int
    name: str
    coordinates: GeoPoint
    administrative_unit_name: str
    country_name: str
    country_code: str

    def __str__(self):
        return f"{self.geonameid}: {self.name}, {self.administrative_unit_name}, {self.country_code}"