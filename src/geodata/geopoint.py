from typing import Annotated, TypedDict, Literal, Sequence

from pydantic import BeforeValidator, WrapValidator

GeoPoint = Sequence[float]


class MongoGeoPoint(TypedDict):
    type: Literal["Point"]
    coordinates: GeoPoint


def _adapt_geo_point(value: MongoGeoPoint | GeoPoint, handler) -> GeoPoint:
    if isinstance(value, dict):
        return value["coordinates"]
    return handler(value)


GeoPointType = Annotated[GeoPoint, WrapValidator(_adapt_geo_point)]
