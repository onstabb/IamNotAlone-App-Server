from datetime import datetime

from mongoengine import (
    StringField,
    BooleanField,
    EnumField,
    ListField,
    URLField,
    EmbeddedDocumentField,
    DateTimeField,
    ReferenceField,
)

from datehelpers import get_aware_datetime_now
from models import BaseDocument
from userprofile.models import UserProfile
from security import create_access_token, get_token_expiration_from_now, verify_password
from users.enums import UserRole


class User(BaseDocument):
    phone_number = StringField(required=True, unique=True) # type: str
    password = StringField(required=True)  # type: str
    role = EnumField(UserRole, default=UserRole.USER, required=True)
    profile = EmbeddedDocumentField(UserProfile, null=True,)   # type: UserProfile | None
    banned = BooleanField(default=False)  # type: bool
    is_active = BooleanField(default=True)    # type: bool
    photo_urls = ListField(URLField())  # type: list[str]

    last_online = DateTimeField(default=get_aware_datetime_now) # type: datetime
    events = ListField(ReferenceField("Event")) # type: list


    @property
    def token(self) -> tuple[str, datetime]:
        expires_at = get_token_expiration_from_now()
        return create_access_token(self.id, expires_at), expires_at

    def check_password(self, password: str | bytes) -> bool:
        return verify_password(password, self.password)

