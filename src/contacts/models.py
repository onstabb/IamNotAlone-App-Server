from mongoengine import ReferenceField, EnumField

from src.contacts.enums import ContactState
from src.models import BaseDocument


CONTACT_RESULT_TABLE = (
    (ContactState.WAIT,     ContactState.WAIT,          ContactState.REFUSED, ContactState.BLOCKED),
    (ContactState.WAIT,     ContactState.ESTABLISHED,   ContactState.REFUSED, ContactState.BLOCKED),
    (ContactState.REFUSED,  ContactState.REFUSED,       ContactState.REFUSED, ContactState.BLOCKED),
    (ContactState.BLOCKED,  ContactState.BLOCKED,       ContactState.BLOCKED, ContactState.BLOCKED),
)


class ProfileContact(BaseDocument):
    initializer = ReferenceField('Profile', required=True)
    respondent = ReferenceField('Profile', required=True)
    initializer_state = EnumField(ContactState, required=True, default=ContactState.WAIT)  # type: ContactState
    respondent_state = EnumField(ContactState, required=True, default=ContactState.WAIT)  # type: ContactState
    status = EnumField(ContactState, required=True, default=ContactState.WAIT)  # type: ContactState

    @property
    def is_finalized(self) -> bool:
        return self.status in ContactState.finalized_states()


    @property
    def is_established(self) -> bool:
        return self.status == ContactState.ESTABLISHED
