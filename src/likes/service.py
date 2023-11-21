from contacts.enums import ContactState
from contacts.models import Contact
from users.models import User


def get_likes_for_user(user: User) -> list[Contact]:
    """
     Retrieve a list of users who have liked the specified user based on the contact collection.

    :param user: The specified user for whom likes are to be retrieved.
    :return: A list of users who have liked the specified user.

    Note: The 'respondent' field in the contacts is excluded from the result for performance purpose.
    """

    result = Contact.objects(
        respondent=user, initiator_state=ContactState.ESTABLISHED, status=None
    ).exclude("respondent")
    return list(result)
