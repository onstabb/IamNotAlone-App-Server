from mongoengine import (
    Q as Query,     # noqa
    DoesNotExist
)

from contacts.enums import ContactState
from contacts.models import Contact, CONTACT_RESULT_TABLE, Message
from contacts.schemas import ContactStateIn, ContactCreateDataIn, MessageIn
from users.models import User


def get_contacts_for_user(user: User, *, limit: int = 0, **filters) -> list[dict]:
    pipeline = [
        {
            "$match": {
                "$and": [
                    {"$or": [{"initiator": user.id}, {"respondent": user.id}]},
                    filters,
                ]
            }
        },
        {
            "$addFields": {
                "opposite_user": {
                    "$cond": {
                        "if": {"$eq": ["$initiator", user.id]},
                        "then": "$respondent",
                        "else": "$initiator"
                    }
                }
            }
        },
        {
            "$lookup": {
                "from": "user",
                "localField": "opposite_user",
                "foreignField": "_id",
                "as": "opposite_user"
            }
        },
        {"$unwind": "$opposite_user"},
        {
            "$match": {"opposite_user.is_active": True, "opposite_user.banned": False, },
        },
    ]

    if limit:
        pipeline.append({"$limit": limit})

    result = list(Contact.objects.aggregate(pipeline))
    return result


def get_contact_by_users_pair(user: User, target_user: User) -> Contact | None:
    """
    Retrieve a Contact instance for the given pair of users.

    :param user: The first user in the pair.
    :param target_user: The second user in the pair.
    :return: A Contact instance if it exists.

    Note: if a contact is found, this function updates the Contact instance by setting
    the appropriate user ID based on the role of the provided 'user' in the contact. If 'user'
    is the respondent, the 'respondent' attribute in the Contact instance is set to the user's ID.
    If 'user' is the initiator, the 'initiator' attribute is set to the user's ID.
    """

    query = (
            (Query(initiator=user) & Query(respondent=target_user)) |
            (Query(respondent=user) & Query(initiator=target_user))
    )
    try:
        contact: Contact = Contact.objects.get(query)
    except DoesNotExist:
        return None

    # From this we cand understand who is target user
    if user == contact.respondent:
        contact.respondent = user.id
    else:
        contact.initiator = user.id

    return contact


def create_contact_by_initiator(initiator: User, respondent: User, data_in: ContactCreateDataIn) -> Contact:
    contact = Contact(initiator=initiator, respondent=respondent, initiator_state=data_in.action)
    contact.status = get_contact_status(contact.respondent_state, contact.initiator_state)
    contact.save()
    return contact


def update_contact_status(contact_state_data: ContactStateIn, user: User, contact: Contact) -> Contact:
    if contact.initiator == user:
        contact.initiator_state = contact_state_data.action

    elif contact.respondent == user:
        contact.respondent_state = contact_state_data.action

    contact.status = get_contact_status(contact.respondent_state, contact.initiator_state)
    contact.save()
    return contact


def create_message(contact: Contact, sender: User, message_in: MessageIn) -> Message:
    message = contact.messages.create(sender=sender, text=message_in.text)
    contact.save()
    return message


def get_messages_count_from_sender(contact: Contact, sender: User) -> int:
    if sender.id not in (contact.initiator, contact.respondent):
        raise ValueError(f"Contact does not contain user with {sender.id}")

    return len(contact.messages.filter(sender=sender))


def get_contact_status(state_1: ContactState | None, state_2: ContactState | None) -> ContactState | None:
    enum_list: list[ContactState | None] = [None] + list(ContactState)
    index_1: int = enum_list.index(state_1)
    index_2: int = enum_list.index(state_2)
    return CONTACT_RESULT_TABLE[index_1][index_2]
