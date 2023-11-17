from mongoengine import StringField, ListField, ReferenceField, DateTimeField

from location.models import LocationWithAddressMixin
from models import BaseDocument


class Event(BaseDocument, LocationWithAddressMixin):
    title = StringField(required=True)  # type: str
    description = StringField(required=True)    # type: str

    subscribers = ListField(ReferenceField("User")) # type: list
    start_at = DateTimeField(required=True) # type:
    image_urls = ListField(StringField())   # type: list[str]

    meta = {
        'indexes': ['location.city_id', [("location.current", "2dsphere")], ]
    }
