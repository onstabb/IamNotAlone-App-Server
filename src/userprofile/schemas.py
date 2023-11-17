from pydantic import BaseModel, Field, AliasChoices, constr, model_validator

from location.geopoint import GeoPoint
from location.schemas import LocationProjectBase
from userprofile import config as model_config
from userprofile.dateofbirth import DateOfBirth, Age

from userprofile.enums import Gender, ResidenceLength, ResidencePlan


ProfileName = constr(
    max_length=model_config.NAME_MAX_LENGTH, min_length=model_config.NAME_MIN_LENGTH
)
ProfileDescription = constr(
    max_length=model_config.DESCRIPTION_MAX_LENGTH, min_length=model_config.DESCRIPTION_MIN_LENGTH
)


class LocationIn(LocationProjectBase):
    current: GeoPoint | None = None

    @model_validator(mode='after')
    def set_current_coordinates(self) -> 'LocationIn':
        if self.current is None:
            self.current = self.city.coordinates
        return self


class LocationOut(LocationProjectBase):
    pass


class UserProfileBase(BaseModel):
    name: ProfileName
    gender: Gender
    gender_preference: Gender | None = None
    description: ProfileDescription
    residence_length: ResidenceLength
    residence_plan: ResidencePlan


class PrivateUserProfileIn(UserProfileBase):
    birthday: DateOfBirth
    location: LocationIn


class PrivateUserProfileOut(PrivateUserProfileIn):
    pass


class PublicUserProfileOut(UserProfileBase):
    age: Age = Field(validation_alias=AliasChoices("birthday", "age"))
    location: LocationOut