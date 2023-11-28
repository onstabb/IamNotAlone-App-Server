from mongoengine import PointField, IntField


from location.geopoint import GeoPoint, MongoGeoPoint


class CityIdField(IntField):
    pass


class LocationMixin:

    city_id = CityIdField(required=True)    # type: int
    location = PointField(auto_index=True, required=True)  # type: GeoPoint

    @property
    def geo_json(self) -> MongoGeoPoint:
        if isinstance(self.location, dict):
            return self.location
        return {"type": "Point", "coordinates": self.location}
