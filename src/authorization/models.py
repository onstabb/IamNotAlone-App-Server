from mongoengine import StringField, BooleanField, ReferenceField

from models import BaseDocument


class User(BaseDocument):
    phone_number = StringField(required=True, unique=True)
    password: str = StringField(required=True)
    banned: bool = BooleanField(required=True, default=False)
    profile = ReferenceField('Profile', null=True)
