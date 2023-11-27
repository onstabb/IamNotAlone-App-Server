import typing

from pydantic import BaseModel, Field, AliasChoices, constr, model_validator

from location.geopoint import GeoPoint
from location.schemas import LocationProjectBase
from userprofile import config as model_config
from userprofile.birthdate import BirthDate, Age

from userprofile.enums import Gender, ResidenceLength, ResidencePlan


ProfileName = constr(
    max_length=model_config.NAME_MAX_LENGTH, min_length=model_config.NAME_MIN_LENGTH
)
ProfileDescription = constr(
    max_length=model_config.DESCRIPTION_MAX_LENGTH, min_length=model_config.DESCRIPTION_MIN_LENGTH
)


class UserProfileBase(LocationProjectBase):
    name: ProfileName
    gender: Gender
    gender_preference: Gender | None = None
    description: ProfileDescription
    residence_length: ResidenceLength
    residence_plan: ResidencePlan



class PrivateUserProfileIn(UserProfileBase):
    birthdate: BirthDate
    location: GeoPoint | None = None

    @model_validator(mode='after')
    def set_current_coordinates(self) -> typing.Self:
        if self.location is None:
            self.location = self.city.coordinates
        return self


class PrivateUserProfileOut(PrivateUserProfileIn):
    pass


class PublicUserProfileOut(UserProfileBase):
    age: Age = Field(validation_alias=AliasChoices("birthdate", "age"))

