from datetime import datetime
from functools import cached_property

from pydantic import AliasChoices, BaseModel, Field, constr, computed_field

from contacts import config
from contacts.enums import ContactState
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
    opposite_user: UserPublicOut | None = Field(exclude=True, default=None)
    created_at: DateTimeFromObjectId = Field(validation_alias=AliasChoices("_id", "id"), )

    @computed_field
    @cached_property
    def user(self) -> UserPublicOut | None:
        """ This is the opposite user resolver for particular user """
        if self.opposite_user:
            return self.opposite_user
        if isinstance(self.initiator, UserPublicOut) and isinstance(self.respondent, PydanticObjectId):
            return self.initiator
        elif isinstance(self.respondent, UserPublicOut) and isinstance(self.initiator, PydanticObjectId):
            return self.respondent

        return None


class ContactOut(ContactBaseOut):
    status: ContactState | None
    messages: list[MessageOut]


class ContactStateIn(BaseModel):
    action: ContactState


class ContactCreateDataIn(ContactStateIn):
    user_id: PydanticObjectId


