from datetime import datetime, timezone
from typing import Any, Self, Annotated

from pydantic import AliasChoices, BaseModel, Field, constr, model_validator, AfterValidator

from contacts import config
from contacts.enums import ContactState, ContactUpdateAction
from models import PydanticObjectId, DateTimeFromObjectId
from users.schemas import UserPublicOut


UtcDatetime = Annotated[datetime, AfterValidator(lambda value: value.astimezone(timezone.utc))]


class MessageBase(BaseModel):
    text: constr(max_length=config.MESSAGE_MAX_LENGTH, min_length=1)


class MessageIn(MessageBase):
    pass


class MessageOut(MessageBase):
    sender: PydanticObjectId | UserPublicOut
    date: UtcDatetime = Field(validation_alias="created_at")


class ContactBaseOut(BaseModel):
    initiator: UserPublicOut | PydanticObjectId = Field(exclude=True)
    respondent: UserPublicOut | PydanticObjectId = Field(exclude=True)
    initiator_last_update_at: UtcDatetime = Field(exclude=True)
    respondent_last_update_at: UtcDatetime | None = Field(exclude=True)

    opposite_user: UserPublicOut | None = None
    opposite_user_last_update_at: UtcDatetime | None = None
    last_update_at: UtcDatetime | None = None
    created_at: DateTimeFromObjectId = Field(validation_alias=AliasChoices("_id", "id"),)

    @model_validator(mode="after")
    def assign_opposite_user(self) -> Self:
        """ This is the opposite user resolver for particular user """
        if self.opposite_user:
            return self
        if isinstance(self.initiator, UserPublicOut) and isinstance(self.respondent, PydanticObjectId):
            self.opposite_user = self.initiator
            self.opposite_user_last_update_at = self.initiator_last_update_at
            self.last_update_at = self.respondent_last_update_at
        elif isinstance(self.respondent, UserPublicOut) and isinstance(self.initiator, PydanticObjectId):
            self.opposite_user = self.respondent
            self.opposite_user_last_update_at = self.respondent_last_update_at
            self.last_update_at = self.initiator_last_update_at
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


