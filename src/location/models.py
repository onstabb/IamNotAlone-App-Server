from mongoengine import PointField, IntField, StringField


from location.geopoint import GeoPoint, MongoGeoPoint


class LocationMixin:

    city_id = IntField(required=True)    # type: int
    location = PointField(auto_index=True, required=True)  # type: GeoPoint

    @property
    def geo_json(self) -> MongoGeoPoint:
        if isinstance(self.location, dict):
            return self.location
        return {"type": "Point", "coordinates": self.location}

