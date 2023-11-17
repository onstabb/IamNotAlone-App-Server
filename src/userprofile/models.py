from datetime import date
from mongoengine import EmbeddedDocument, EnumField, StringField, DateField

from location.models import LocationMixin
from userprofile.enums import Gender, ResidenceLength, ResidencePlan


class UserProfile(EmbeddedDocument, LocationMixin):
    name = StringField(required=True)   # type: str
    gender = EnumField(enum=Gender, required=True)  # type: Gender
    gender_preference = EnumField(enum=Gender, default=None, null=True)  # type: Gender
    birthdate = DateField(required=True)   # type: date
    description = StringField(required=True)   # type: str
    residence_plan = EnumField(enum=ResidencePlan, required=True)   # type: ResidencePlan
    residence_length = EnumField(enum=ResidenceLength, required=True)   # type: ResidenceLength

