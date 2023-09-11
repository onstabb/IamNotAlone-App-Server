__all__ = ('CityGeonames', 'CityRow')

from typing import Any, Callable, Annotated

from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

from src.geodata.database import GeoNamesSqlite
from src.geodata.basetypes import CityRow


# FIXME: Maybe there should be two different types for model in and out
class _CityPydanticAnnotation:

    @classmethod
    def validate_from_int(cls, value: int) -> CityRow:
        geodata: GeoNamesSqlite = GeoNamesSqlite.get_instance()

        city_row: CityRow | None = geodata.get_city(value)
        if not city_row:
            raise ValueError(f"City with geonameid {value} doesn't exists")
        return city_row

    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            _source_type: Any,
            _handler: Callable[[Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:

        from_int_schema = core_schema.chain_schema(
            [
                core_schema.int_schema(),
                core_schema.no_info_plain_validator_function(cls.validate_from_int),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_int_schema,
            python_schema=core_schema.union_schema(
                [
                    # core_schema.is_instance_schema(CityRow,),
                    core_schema.no_info_plain_validator_function(CityRow.model_validate),
                    from_int_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda instance: instance.geonameid),
        )

    @classmethod
    def __get_pydantic_json_schema__(
            cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        # Use the same schema that would be used for `int`
        json_schema = handler(core_schema.int_schema())
        json_schema.update(example=3081368)  # Wroclaw
        return json_schema



CityGeonames = Annotated[CityRow, _CityPydanticAnnotation]
