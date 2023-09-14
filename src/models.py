import typing
from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId
from mongoengine import (
    Document,
    DoesNotExist, PointField
)
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler, PlainSerializer
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from pydantic_core.core_schema import ValidationInfo

if typing.TYPE_CHECKING:
    from src.geodata.geopoint import GeoPoint

class PydanticObjectId(ObjectId):

    @classmethod
    def validate(cls, value: typing.AnyStr | ObjectId, _validation_info: ValidationInfo) -> typing.Self:
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        try:
            return cls(value)
        except InvalidId:
            raise ValueError("id doesn't match ObjectId type")

    @classmethod
    def __get_pydantic_core_schema__(
            cls, _source: typing.Any, _handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            serialization=core_schema.plain_serializer_function_ser_schema(lambda instance: str(instance)),
            python_schema=core_schema.general_plain_validator_function(cls.validate),
            json_schema=core_schema.str_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(
            cls, schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(schema)
        json_schema.update(type="string", example="507f191e810c19729de860ea")
        return json_schema


class BaseDocument(Document):
    meta = {"abstract": True}

    @classmethod
    def get_one(cls, **kwargs) -> typing.Self | None:
        try:
            obj = cls.objects.get(**kwargs)
            return obj
        except DoesNotExist:
            pass

        return None

    @property
    def created_at(self) -> datetime:
        return self.id.generation_time


SerializeDocToId = PlainSerializer(lambda doc: doc.id, return_type=str, when_used="json")

class LocationPointMixin:
    coordinates: 'GeoPoint' = PointField(required=True, )
