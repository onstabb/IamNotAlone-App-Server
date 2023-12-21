from mongoengine import (
    Q as Query,     # noqa
    DoesNotExist
)

from contacts.enums import ContactState, ContactUpdateAction
from contacts.models import Contact, Message
from contacts.schemas import ContactCreateDataIn, MessageIn
from datehelpers import get_aware_datetime_now
from users.models import User


def get_contacts_by_user(user: User, *, limit: int = 0, **filters) -> list[dict]:
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
                },
                "last_update_at": {
                    "$cond": {
                        "if": {"$eq": ["$initiator", user.id]},
                        "then": "$initiator_last_update_at",
                        "else": "$respondent_last_update_at",
                    }
                }
            }
        },
        {
            "$addFields": {
                "opposite_user_last_update_at": {
                    "$cond": {
                        "if": {"$eq": ["$initiator", "$opposite_user"]},
                        "then": "$initiator_last_update_at",
                        "else": "$respondent_last_update_at"
                    }
                },
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


def get_contact_by_users_pair(current_user: User, target_user: User) -> Contact | None:
    """
    Retrieve a Contact instance for the given pair of users.

    :param current_user: The first user in the pair.
    :param target_user: The second user in the pair.
    :return: A Contact instance if it exists.
    """

    query = (
        (Query(initiator=current_user) & Query(respondent=target_user))
        | (Query(respondent=current_user) & Query(initiator=target_user))
    )
    try:
        contact: Contact = Contact.objects.get(query)
    except DoesNotExist:
        return None

    return contact


def create_contact_by_initiator(initiator: User, respondent: User, data_in: ContactCreateDataIn) -> Contact:
    contact = Contact(initiator=initiator, respondent=respondent, initiator_state=data_in.state)
    contact.save()
    return contact


def update_contact(
        contact_update_action: ContactUpdateAction, user: User, contact: Contact, save: bool = True
) -> Contact:
    user_role = ""
    if contact.initiator == user:
        user_role = "initiator"
    elif contact.respondent == user:
        user_role = "respondent"
    else:
        ValueError(f"Contact does not contain user {user.id}")

    if contact_update_action != ContactUpdateAction.SEEN:
        action_states = {
            ContactUpdateAction.BLOCK: ContactState.BLOCKED,
            ContactUpdateAction.REFUSE: ContactState.REFUSED,
            ContactUpdateAction.ESTABLISH: ContactState.ESTABLISHED,
        }
        if state := action_states.get(contact_update_action):
            setattr(contact, f"{user_role}_state", state)
    else:
        setattr(contact, f"{user_role}_last_update_at", get_aware_datetime_now())

    if save:
        contact.save()

    return contact


def create_message(contact: Contact, sender: User, message_in: MessageIn) -> Message:
    message = contact.messages.create(sender=sender, text=message_in.text)
    update_contact(ContactUpdateAction.SEEN, sender, contact, save=False)
    contact.save()
    return message


def get_messages_count_from_sender(contact: Contact, sender: User) -> int:
    if sender not in (contact.initiator, contact.respondent):
        raise ValueError(f"Contact does not contain user with {sender.id}")

    return len(contact.messages.filter(sender=sender))

