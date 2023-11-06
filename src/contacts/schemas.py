from pydantic import BaseModel, computed_field, Field, AliasChoices

from contacts.enums import ContactState
from models import PydanticObjectId
from profiles.schemas import PublicProfileSimplified


class ContactOut(BaseModel):

    id: PydanticObjectId = Field(validation_alias=AliasChoices("_id", "id"))
    initiator: PublicProfileSimplified
    respondent: PublicProfileSimplified
    status: ContactState | None


class ContactStateIn(BaseModel):
    action: ContactState


class ContactCreateDataIn(ContactStateIn):
    profile_id: PydanticObjectId
