from pydantic import BaseModel, HttpUrl, Field, AliasChoices

from models import PydanticObjectId
from userprofile.schemas import PrivateUserProfileOut, PublicUserProfileOut


class UserProjectBase(BaseModel):
    id: PydanticObjectId = Field(validation_alias=AliasChoices("id", "_id"))
    photo_urls: list[HttpUrl]


class UserPrivateOut(UserProjectBase):
    profile: PrivateUserProfileOut | None


class UserPublicOut(UserProjectBase):
    profile: PublicUserProfileOut
