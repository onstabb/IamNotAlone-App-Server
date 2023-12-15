from datetime import datetime
from typing import TYPE_CHECKING, Self

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

if TYPE_CHECKING:
    from users.models import User


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
    initiator = ReferenceField('User', required=True)   # type: User
    respondent = ReferenceField('User', required=True)  # type: User
    initiator_state = EnumField(ContactState)  # type: ContactState
    respondent_state = EnumField(ContactState, null=True, required=False)  # type: ContactState | None
    initiator_last_update_at = DateTimeField(default=get_aware_datetime_now)  # type: datetime
    respondent_last_update_at = DateTimeField(required=False, null=True) # type: datetime | None
    status = EnumField(ContactState, null=True, required=False)  # type: ContactState | None
    messages = EmbeddedDocumentListField(Message)   # type: EmbeddedDocumentList[Message]

    meta = {
        "indexes": [{"fields": ["initiator", "respondent"], "unique": True}]
    }

    def __init__(self, *args, **values) -> None:
        super().__init__(*args, **values)
        self._initial_initiator_state = self.initiator_state
        self._initial_respondent_state = self.respondent_state

    @staticmethod
    def get_contact_status(state_1: ContactState | None, state_2: ContactState | None) -> ContactState | None:
        enum_list: list[ContactState | None] = [None] + list(ContactState)
        index_1: int = enum_list.index(state_1)
        index_2: int = enum_list.index(state_2)
        return CONTACT_RESULT_TABLE[index_1][index_2]

    def clean(self) -> None:
        if self.respondent_last_update_at is None and self.respondent_state:
            self.respondent_last_update_at = get_aware_datetime_now()

        if self._initial_initiator_state != self.initiator_state:
            self._initial_initiator_state = self.initiator_state
            self.initiator_last_update_at = get_aware_datetime_now()
        elif self._initial_respondent_state != self.respondent_state:
            self._initial_respondent_state = self.respondent_state
            self.respondent_last_update_at = get_aware_datetime_now()

        self.status = self.get_contact_status(self.initiator_state, self.respondent_state)
        return

    @property
    def established(self) -> bool:
        return self.status == ContactState.ESTABLISHED

    def reset_field_to_dbref(self, field_name: str) -> Self:
        document = getattr(self, field_name)
        setattr(self, field_name, document.to_dbref())
        return self

    def reset_current_user(self, current_user: 'User') -> Self:
        """
        This function updates the self instance by setting the appropriate user ID based on the role of the provided 'user' in the contact.
        If 'user' is the respondent, the 'respondent' attribute in the self instance is set to the user's ID.
        If 'user' is the initiator, the 'initiator' attribute is set to the user's ID.
        The purpose of this function is a resolving who is the opposite user for current user.

        :param current_user: The user for which we want to define the opposite user.
        :return: self instance
        :raise ValueError: Contact does not contain this user
        """

        if current_user == self.initiator:
            self.initiator = current_user.id
        elif current_user == self.respondent:
            self.respondent = current_user.id
        else:
            ValueError(f"Contact does not contain user {current_user.id}")

        return self

