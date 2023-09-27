from pydantic import BaseModel


from contacts.enums import ContactState
from models import PydanticObjectId


class RateIn(BaseModel):
    profile_id: PydanticObjectId
    contact: ContactState

