from datetime import datetime
from functools import cached_property
from typing import Any, Self

from bson import ObjectId
from pydantic import AliasChoices, BaseModel, Field, constr, computed_field, model_validator

from contacts import config
from contacts.enums import ContactState, ContactUpdateAction
from models import PydanticObjectId, DateTimeFromObjectId
from users.schemas import UserPublicOut


class MessageBase(BaseModel):
    text: constr(max_length=config.MESSAGE_MAX_LENGTH, min_length=1)


class MessageIn(MessageBase):
    pass


class MessageOut(MessageBase):
    sender: PydanticObjectId | UserPublicOut
    date: datetime = Field(validation_alias="created_at")


class ContactBaseOut(BaseModel):
    initiator: UserPublicOut | PydanticObjectId = Field(exclude=True)
    respondent: UserPublicOut | PydanticObjectId = Field(exclude=True)
    initiator_last_update_at: datetime = Field(exclude=True)
    respondent_last_update_at: datetime | None = Field(exclude=True)

    opposite_user: UserPublicOut | None = None
    opposite_user_last_update_at: datetime | None = None
    created_at: DateTimeFromObjectId = Field(validation_alias=AliasChoices("_id", "id"), )

    @model_validator(mode="after")
    def assign_opposite_user(self) -> Self:
        """ This is the opposite user resolver for particular user """
        if self.opposite_user:
            return self
        if isinstance(self.initiator, UserPublicOut) and isinstance(self.respondent, PydanticObjectId):
            self.opposite_user = self.initiator
            self.opposite_user_last_update_at = self.initiator_last_update_at
        elif isinstance(self.respondent, UserPublicOut) and isinstance(self.initiator, PydanticObjectId):
            self.opposite_user = self.respondent
            self.opposite_user_last_update_at = self.respondent_last_update_at
        else:
            ValueError("Incorrect input")

        return self


class ContactOut(ContactBaseOut):
    status: ContactState | None
    messages: list[MessageOut]


class ContactUpdateIn(BaseModel):
    action: ContactUpdateAction


class ContactCreateDataIn(BaseModel):
    state: ContactState
    user_id: PydanticObjectId


