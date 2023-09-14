from pydantic import BaseModel, constr, Field, AliasChoices, conlist, HttpUrl

from src.files.imageurl import ImageUrl
from src.geodata.citygeonames import CityGeonames
from src.geodata.geopoint import GeoPointType
from src.models import PydanticObjectId
from src.profiles.birthday import DateOfBirth, Age
from src.profiles import config as model_config
from src.profiles.enums import Gender, ResidenceLength, ResidencePlan


ProfileName = constr(max_length=model_config.NAME_MAX_LENGTH, min_length=model_config.NAME_MIN_LENGTH)
ProfileDescription = constr(
    max_length=model_config.DESCRIPTION_MAX_LENGTH, min_length=model_config.DESCRIPTION_MIN_LENGTH
)


class _ProfileBase(BaseModel):
    name: ProfileName
    gender: Gender
    gender_preference: Gender
    description: ProfileDescription
    residence_length: ResidenceLength
    residence_plan: ResidencePlan

class _ProfileOutBase(_ProfileBase):
    id: PydanticObjectId = Field(validation_alias=AliasChoices("id", "_id"))
    photo_urls: list[HttpUrl]
    current_city_id: int | CityGeonames = Field(validation_alias="current_city")
    native_city_id: int | CityGeonames = Field(validation_alias="native_city")


class PrivateProfileIn(_ProfileBase):
    birthday: DateOfBirth
    coordinates: GeoPointType | None
    photo_urls: conlist(ImageUrl, max_length=model_config.MAX_PROFILE_PHOTOS, min_length=1)
    current_city: CityGeonames = Field(
        serialization_alias="current_city_id",
        validation_alias=AliasChoices("current_city_id", "current_city")
    )
    native_city: CityGeonames | None = Field(
        serialization_alias="native_city_id",
        validation_alias=AliasChoices("native_city_id", "native_city")
    )


class PrivateProfileOut(_ProfileOutBase):
    birthday: DateOfBirth
    photo_urls: list[HttpUrl]


class PublicProfileOut(_ProfileOutBase):
    age: Age = Field(validation_alias="birthday")
