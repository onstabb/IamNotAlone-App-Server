import datetime
from typing import Annotated

from pydantic import BaseModel, Field, constr, HttpUrl, ConfigDict, AliasChoices

from messages import config
from messages.enums import MessageType
from models import PydanticObjectId, SerializeDocToId
from profiles.schemas import PublicProfileOut, PublicProfileSimplified


PublicProfileOutId = Annotated[PublicProfileOut, SerializeDocToId]


class MessageIn(BaseModel):
    recipient_id: PydanticObjectId
    content_text: constr(max_length=config.MESSAGE_MAX_LENGTH, min_length=1)


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PydanticObjectId = Field(validation_alias=AliasChoices("id", "_id"))
    sender: PublicProfileSimplified
    recipient: PublicProfileSimplified
    date: datetime.datetime = Field(validation_alias="created_at",)
    message_type: MessageType
    content_text: str | None


class DialogItemOut(BaseModel):
    latest_message: MessageOut
    profile_id: PydanticObjectId = Field(validation_alias="_id")
    profile_name: str
    profile_main_photo_url: HttpUrl
