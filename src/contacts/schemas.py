from pydantic import BaseModel, field_validator


from src.contacts.enums import ContactState
from src.models import PydanticObjectId


class RateIn(BaseModel):
    profile_id: PydanticObjectId
    contact: ContactState

    @field_validator("contact", mode="after")
    def filter_contact_state(cls, v: ContactState) -> ContactState:
        if v == ContactState.WAIT:
            raise ValueError(f"value `{v}` is not allowed")
        return v
