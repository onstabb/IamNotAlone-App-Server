from mongoengine import StringField, ListField, ReferenceField, DateTimeField, IntField

from geodata.models import LocationMixin
from models import BaseDocument


class Event(BaseDocument, LocationMixin):
    title = StringField(required=True)
    description = StringField(required=True)
    address = StringField(required=True)
    city_id = IntField(required=True)
    subscribers = ListField(ReferenceField("Profile"))
    start_at = DateTimeField(required=True)
    image_urls = ListField(StringField())

    meta = {
        'indexes': ['city_id'],
    }
