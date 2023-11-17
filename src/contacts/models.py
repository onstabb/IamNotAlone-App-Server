from datetime import datetime

from mongoengine import (
    ReferenceField,
    EnumField,
    EmbeddedDocument,
    StringField,
    DateTimeField,
    EmbeddedDocumentListField,
    LazyReferenceField
)
from mongoengine.base import EmbeddedDocumentList

from contacts.enums import ContactState
from datehelpers import get_aware_datetime_now
from models import BaseDocument


    # None                  # established               # refused             # blocked
CONTACT_RESULT_TABLE = (
    (None,                  None,                       ContactState.REFUSED, ContactState.BLOCKED),    # None
    (None,                  ContactState.ESTABLISHED,   ContactState.REFUSED, ContactState.BLOCKED),    # established
    (ContactState.REFUSED,  ContactState.REFUSED,       ContactState.REFUSED, ContactState.BLOCKED),    # refused
    (ContactState.BLOCKED,  ContactState.BLOCKED,       ContactState.BLOCKED, ContactState.BLOCKED),    # blocked
)


class Message(EmbeddedDocument):
    text = StringField(required=True)   # type: str
    sender = LazyReferenceField('User')
    created_at = DateTimeField(default=get_aware_datetime_now, required=True)   # type: datetime


class Contact(BaseDocument):
    initiator = ReferenceField('User', required=True)
    respondent = ReferenceField('User', required=True)
    initiator_state = EnumField(ContactState, null=True)  # type: ContactState | None
    respondent_state = EnumField(ContactState, null=True)  # type: ContactState | None
    status = EnumField(ContactState, null=True)  # type: ContactState | None
    messages = EmbeddedDocumentListField(Message)   # type: EmbeddedDocumentList[Message]

    meta = {
        "indexes": [{"fields": ["initiator", "respondent"], "unique": True}]
    }

    @property
    def established(self) -> bool:
        return self.status == ContactState.ESTABLISHED
