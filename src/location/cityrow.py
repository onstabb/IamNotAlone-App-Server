from pydantic import BaseModel, ConfigDict

from location.geopoint import GeoPoint


class CityRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    longitude: float
    latitude: float
    administrative_name: str
    country_name: str

    @property
    def coordinates(self) -> list[float, float]:
        return [self.longitude, self.latitude]

    def __str__(self):
        return f"{self.id}: {self.name}, {self.administrative_name}, {self.country_name}"