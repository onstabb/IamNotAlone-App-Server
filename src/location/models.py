from mongoengine import EmbeddedDocument, PointField, EmbeddedDocumentField, IntField, StringField


from location.geopoint import GeoPoint, MongoGeoPoint


class Location(EmbeddedDocument):

    meta = {'allow_inheritance': True}

    city_id = IntField()    # type: int
    current = PointField(auto_index=False)  # type: GeoPoint

    @property
    def current_geo_json(self) -> MongoGeoPoint:
        if isinstance(self.current, dict):
            return self.current
        return {"type": "Point", "coordinates": self.current}


class LocationWithAddress(Location):
    address = StringField(required=True)    # type: str


class LocationMixin:
    location = EmbeddedDocumentField(Location, required=True, default=Location) # type: Location


class LocationWithAddressMixin:
    location = EmbeddedDocumentField(LocationWithAddress, required=True, default=LocationWithAddress)    # type: LocationWithAddress
