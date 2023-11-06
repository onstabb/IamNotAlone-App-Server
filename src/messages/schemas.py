import datetime
from typing import Annotated

from pydantic import BaseModel, Field, constr, ConfigDict, AliasChoices

from messages import config
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
    content_text: str

