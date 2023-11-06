from mongoengine import EmbeddedDocument, PointField, EmbeddedDocumentField


class Location(EmbeddedDocument):
    city_coordinates = PointField()
    coordinates = PointField()


class LocationMixin:
    location = EmbeddedDocumentField(Location, required=True, default=Location)
