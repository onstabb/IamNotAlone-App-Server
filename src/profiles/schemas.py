from typing import Annotated

from pydantic import BaseModel, constr, Field, AliasChoices, HttpUrl, ConfigDict, WrapValidator

from geodata.citygeonames import CityGeonames
from geodata.geopoint import GeoPointType
from models import PydanticObjectId
from profiles.birthday import DateOfBirth, Age
from profiles import config as model_config
from profiles.enums import Gender, ResidenceLength, ResidencePlan


ProfileName = constr(max_length=model_config.NAME_MAX_LENGTH, min_length=model_config.NAME_MIN_LENGTH)
ProfileDescription = constr(
    max_length=model_config.DESCRIPTION_MAX_LENGTH, min_length=model_config.DESCRIPTION_MIN_LENGTH
)
MainPhoto = Annotated[
    str,
    WrapValidator(lambda value, handler: value[0] if isinstance(value, list) and len(value) > 0 else handler(value))
]


class _ProfileBase(BaseModel):
    name: ProfileName


class _ProfileFullBase(_ProfileBase):
    gender: Gender
    gender_preference: Gender | None = None
    description: ProfileDescription
    residence_length: ResidenceLength
    residence_plan: ResidencePlan


class _ProfileOutBase(_ProfileBase):
    id: PydanticObjectId = Field(validation_alias=AliasChoices("id", "_id"))


class _ProfileFullOutBase(_ProfileOutBase, _ProfileFullBase):
    photo_urls: list[HttpUrl]
    current_city_id: int | CityGeonames
    native_city_id: int | None


class PrivateProfileIn(_ProfileFullBase):
    birthday: DateOfBirth
    coordinates: GeoPointType | None = None
    current_city: CityGeonames = Field(
        serialization_alias="current_city_id",
        validation_alias="current_city_id"
    )
    native_city: CityGeonames | None = Field(
        serialization_alias="native_city_id",
        validation_alias="native_city_id",
        default=None
    )


class PrivateProfileOut(_ProfileFullOutBase):
    birthday: DateOfBirth


class PublicProfileSimplified(_ProfileOutBase):
    profile_photo_url: MainPhoto = Field(validation_alias="photo_urls")


class PublicProfileOut(_ProfileFullOutBase):
    model_config = ConfigDict(from_attributes=True)

    age: Age = Field(validation_alias=AliasChoices("birthday", "age"))
