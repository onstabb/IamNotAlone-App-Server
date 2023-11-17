from typing import Annotated, TypedDict, Literal, Sequence

from pydantic import WrapValidator


_GeoPoint = Sequence[float]  # longitude, latitude


class MongoGeoPoint(TypedDict):
    type: Literal["Point"]
    coordinates: _GeoPoint


def _adapt_geo_point(value: MongoGeoPoint | _GeoPoint, handler) -> _GeoPoint:
    if isinstance(value, dict):
        return value["coordinates"]
    return handler(value)


# longitude, latitude
GeoPoint = Annotated[_GeoPoint, WrapValidator(_adapt_geo_point)]
