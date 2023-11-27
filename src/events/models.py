from mongoengine import StringField, ListField, ReferenceField, DateTimeField, URLField

from location.models import LocationMixin
from models import BaseDocument


class Event(BaseDocument, LocationMixin):
    title = StringField(required=True)  # type: str
    description = StringField(required=True)    # type: str

    subscribers = ListField(ReferenceField("User")) # type: list
    start_at = DateTimeField(required=True) # type:
    image_urls = ListField(URLField())   # type: list[str]
    address = StringField(required=True)

    meta = {
        'indexes': ['city_id', ]
    }
