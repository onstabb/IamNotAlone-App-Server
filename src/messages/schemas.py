import datetime
from typing import Annotated

from pydantic import BaseModel, Field, constr, HttpUrl

from src.messages import config
from src.messages.enums import MessageType
from src.models import PydanticObjectId, SerializeDocToId
from src.profiles.schemas import PublicProfileOut


PublicProfileOutId = Annotated[PublicProfileOut, SerializeDocToId]


class MessageIn(BaseModel):
    recipient_id: PydanticObjectId
    content_text: constr(max_length=config.MESSAGE_MAX_LENGTH, min_length=1)


class MessageOut(BaseModel):
    id: PydanticObjectId
    sender: PublicProfileOutId = Field(serialization_alias="sender_id")
    recipient: PublicProfileOutId = Field(serialization_alias="recipient_id")
    date: datetime.date = Field(validation_alias="created_at",)
    message_type: MessageType
    content_text: str


class DialogItemOut(BaseModel):
    latest_message: MessageOut
    profile_id: PydanticObjectId = Field(validation_alias="_id")
    profile_name: str
    profile_main_photo_url: HttpUrl
