from datetime import datetime

from mongoengine import StringField, DateField, EnumField, ReferenceField, ListField, BooleanField, DateTimeField

from datehelpers import get_aware_datetime_now
from profiles.enums import Gender, ResidencePlan, ResidenceLength
from models import BaseDocument, LocationPointMixin


class Profile(BaseDocument, LocationPointMixin):
    name = StringField(required=True)
    birthday = DateField(required=True)
    gender = EnumField(enum=Gender, required=True)
    gender_preference: Gender | None = EnumField(enum=Gender, default=None, null=True)
    description = StringField(required=True)

    current_city = ReferenceField('City', required=True)
    native_city = ReferenceField('City', null=True)
    residence_plan = EnumField(enum=ResidencePlan, required=True)
    residence_length = EnumField(enum=ResidenceLength, required=True)
    photo_urls = ListField(StringField())

    disabled: bool = BooleanField(default=False)
    last_online: datetime = DateTimeField(default=get_aware_datetime_now)
    events = ListField(ReferenceField("Event"))
