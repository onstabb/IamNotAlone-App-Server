import typing
from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId
from mongoengine import (
    Document,
    DoesNotExist,
)
from mongoengine.base import BaseField, LazyReference
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler, PlainSerializer, BeforeValidator
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


class PydanticObjectId(ObjectId):

    @classmethod
    def validate(cls, value: typing.AnyStr | ObjectId | LazyReference) -> typing.Self:
        if isinstance(value, bytes):
            value = value.decode("utf-8")

        if isinstance(value, LazyReference):
            value = value.id

        try:
            return cls(value)
        except InvalidId:
            raise ValueError("id doesn't match ObjectId type")

    @classmethod
    def __get_pydantic_core_schema__(
            cls, _source: typing.Any, _handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        schema = core_schema.chain_schema(
            [
                core_schema.union_schema(
                    [
                        core_schema.str_schema(),
                        core_schema.is_instance_schema(ObjectId),
                        core_schema.is_instance_schema(LazyReference)
                    ]
                ),
                core_schema.no_info_plain_validator_function(cls.validate)
            ]
        )
        return core_schema.json_or_python_schema(
            serialization=core_schema.plain_serializer_function_ser_schema(lambda instance: str(instance)),
            python_schema=schema,
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

    @classmethod
    def get_field_info(cls) -> dict[str, BaseField]:
        return cls._fields      # noqa

    @property
    def created_at(self) -> datetime:
        return self.id.generation_time


SerializeDocToId = PlainSerializer(lambda doc: doc.id, return_type=str, when_used="json")
DateTimeFromObjectId = typing.Annotated[datetime, BeforeValidator(lambda value: value.generation_time)]
