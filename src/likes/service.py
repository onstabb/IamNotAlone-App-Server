from contacts.enums import ContactState
from contacts.models import Contact
from users.models import User


def get_likes(user: User) -> list[Contact]:
    result = Contact.objects(
        respondent=user, initiator_state=ContactState.ESTABLISHED, status=None
    ).exclude("respondent")
    return list(result)
