from mongoengine import StringField, ReferenceField, BooleanField, EnumField

from messages.enums import MessageType
from models import BaseDocument


class Message(BaseDocument):
    content_text = StringField(null=True)
    sender = ReferenceField("Profile", required=True)
    recipient = ReferenceField("Profile", required=True)
    message_type = EnumField(MessageType, required=True)
    delivered = BooleanField(default=False, required=True)
    has_read = BooleanField(default=False, required=True)

