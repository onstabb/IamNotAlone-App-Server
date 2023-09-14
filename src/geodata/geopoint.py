from typing import Annotated, TypedDict, Literal

from pydantic import BeforeValidator

GeoPoint = tuple[float, float] | list[float]


class MongoGeoPoint(TypedDict):
    type: Literal["Point"]
    coordinates: GeoPoint


def _adapt_geo_point(value: MongoGeoPoint | GeoPoint) -> GeoPoint:
    if isinstance(value, dict):
        return value["coordinates"]
    return value


GeoPointType = Annotated[GeoPoint, BeforeValidator(_adapt_geo_point)]
