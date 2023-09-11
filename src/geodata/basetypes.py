from typing import Annotated, TypedDict, Literal

from pydantic import BaseModel, ConfigDict, BeforeValidator

GeoPoint = tuple[float, float] | list[float]


class MongoGeoPoint(TypedDict):
    type: Literal["Point"]
    coordinates: GeoPoint


def _adapt_geo_point(v: MongoGeoPoint | GeoPoint) -> GeoPoint:
    if isinstance(v, dict):
        return v["coordinates"]
    return v


GeoPointType = Annotated[GeoPoint, BeforeValidator(_adapt_geo_point)]


class CityRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    geonameid: int
    name: str
    coordinates: GeoPointType
    administrative_unit_name: str
    country_name: str
    country_code: str
