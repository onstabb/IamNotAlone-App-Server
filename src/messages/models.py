from mongoengine import StringField, ReferenceField, BooleanField, EnumField

from models import BaseDocument


class Message(BaseDocument):
    content_text = StringField(required=True)
    sender = ReferenceField("Profile", required=True)
    recipient = ReferenceField("Profile", required=True)
    has_read = BooleanField(default=False, required=True)
