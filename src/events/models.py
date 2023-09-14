from mongoengine import StringField, ListField, ReferenceField, DateTimeField

from models import BaseDocument, LocationPointMixin


class Event(BaseDocument, LocationPointMixin):
    title = StringField(required=True)
    description = StringField(required=True)
    address = StringField(required=True)
    city = ReferenceField("City", required=True)
    subscribers = ListField(ReferenceField("Profile"))
    start_at = DateTimeField(required=True)
    image_urls = ListField(StringField())
