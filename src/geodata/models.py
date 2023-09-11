__all__ = ('City',)

from mongoengine import IntField, StringField

from src.models import BaseDocument, LocationPointMixin


class City(BaseDocument, LocationPointMixin):
    geonameid: int = IntField(primary_key=True)
    name: str = StringField(required=True)
    administrative_unit_name: str = StringField(required=True)
    country_name: str = StringField(required=True)
    country_code: str = StringField(required=True)
