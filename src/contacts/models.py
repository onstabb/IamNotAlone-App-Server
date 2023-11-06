from mongoengine import ReferenceField, EnumField

from contacts.enums import ContactState
from models import BaseDocument

    # None                  # established               # refused             # blocked
CONTACT_RESULT_TABLE = (
    (None,                  None,                       ContactState.REFUSED, ContactState.BLOCKED),    # None
    (None,                  ContactState.ESTABLISHED,   ContactState.REFUSED, ContactState.BLOCKED),    # established
    (ContactState.REFUSED,  ContactState.REFUSED,       ContactState.REFUSED, ContactState.BLOCKED),    # refused
    (ContactState.BLOCKED,  ContactState.BLOCKED,       ContactState.BLOCKED, ContactState.BLOCKED),    # blocked
)


class ProfileContact(BaseDocument):
    initiator = ReferenceField('Profile', required=True)
    respondent = ReferenceField('Profile', required=True)
    initiator_state = EnumField(ContactState, null=True)  # type: ContactState | None
    respondent_state = EnumField(ContactState, null=True)  # type: ContactState | None
    status = EnumField(ContactState, null=True)  # type: ContactState | None

    meta = {
        "indexes": [{"fields": ["initiator", "respondent"], "unique": True}]
    }
    @property
    def is_established(self) -> bool:
        return self.status == ContactState.ESTABLISHED
