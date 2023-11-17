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
    return contact.messages.create(sender=sender, text=message_in.text)


def get_messages_count_from_sender(contact: Contact, sender: User) -> int:
    if sender not in (contact.initiator, contact.respondent):
        raise ValueError(f"Contact does not contain user with {sender.id}")

    return len(contact.messages.filter(sender=sender))


def get_contact_status(state_1: ContactState | None, state_2: ContactState | None) -> ContactState | None:
    enum_list: list[ContactState | None] = [None] + list(ContactState)
    index_1: int = enum_list.index(state_1)
    index_2: int = enum_list.index(state_2)
    return CONTACT_RESULT_TABLE[index_1][index_2]


# def get_profile_state(user: User, contact: Contact) -> ContactState | None:
#     if user == contact.initiator:
#         return contact.initiator_state
#     elif user == contact.respondent:
#         return contact.respondent_state
#     else:
#         raise ValueError("Given user must be in this relationship!")

#
# def get_new_established_contacts(profile: User) -> list[dict]:
#
#     pipeline = [
#         # Only established
#         {
#             "$match": {
#                 "$or": [{"respondent": profile.id}, {"initiator": profile.id}],
#                 "status": ContactState.ESTABLISHED
#             }
#         },
#
#         # No common messages
#         {
#             "$lookup": {
#                 "from": "message",
#                 "let": {
#                     "initiatorId": "$initiator",
#                     "respondentId": "$respondent"
#                 },
#                 "pipeline": [
#                     {
#                         "$match": {
#                             "$expr": {
#                                 "$or": [
#                                     {
#                                         "$and": [
#                                             {
#                                                 "$eq": ["$sender", "$$initiatorId"]
#                                             },
#                                             {
#                                                 "$eq": ["$recipient", "$$respondentId"]
#                                             }
#                                         ]
#                                     },
#                                     {
#                                         "$and": [
#                                             {
#                                                 "$eq": ["$sender", "$$respondentId"]
#                                             },
#                                             {
#                                                 "$eq": ["$recipient", "$$initiatorId"]
#                                             }
#                                         ]
#                                     }
#                                 ]
#                             }
#                         }
#                     }
#                 ],
#                 "as": "messages"
#             }
#         },
#         {
#             "$match": {"messages": {"$eq": []}}
#         },
#
#         # Filter disabled
#         {
#             "$lookup": {
#                 "from": "userprofile",
#                 "localField": "initiator",
#                 "foreignField": "_id",
#                 "as": "initiator"
#             }
#         },
#         {
#             "$lookup": {
#                 "from": "userprofile",
#                 "localField": "respondent",
#                 "foreignField": "_id",
#                 "as": "respondent"
#             }
#         },
#         {
#             "$unwind": "$respondent"
#         },
#         {
#             "$unwind": "$initiator"
#         },
#         {
#             "$match": {
#                 "initiator.disabled": False,
#                 "respondent.disabled": False
#             }
#         },
#     ]
#
#     return list(Contact.objects.aggregate(pipeline))
#
#
# def get_profile_likes(profile: User) -> list[dict]:
#     pipeline = [
#         {
#             "$match": {
#                 "respondent": profile.id,
#                 "status": None,
#                 "respondent_state": None,
#                 "initiator_state": ContactState.ESTABLISHED,
#             }
#         },
#
#         # Filter disabled profiles
#         {
#             "$lookup": {
#                 "from": "userprofile",
#                 "localField": "initiator",
#                 "foreignField": "_id",
#                 "as": "initiator"
#             }
#         },
#         {
#             "$lookup": {
#                 "from": "userprofile",
#                 "localField": "respondent",
#                 "foreignField": "_id",
#                 "as": "respondent"
#             }
#         },
#         {
#             "$unwind": "$respondent"
#         },
#         {
#             "$unwind": "$initiator"
#         },
#         {
#             "$match": {
#                 "initiator.disabled": False,
#                 "respondent.disabled": False
#             }
#         },
#     ]
#     return list(Contact.objects.aggregate(pipeline))
#
#
# def get_contacts_for_user(
#         user_id: MongoObjectId, contact_type: ContactType = ContactType.NEW_ESTABLISHED
# ) -> list[dict]:
#
#     match_query = {"$or": [{"initiator": user_id}, {"respondent": user_id}]}
#
#     if contact_type == ContactType.NEW_ESTABLISHED:
#         match_query = {
#             "$and": [
#                 match_query,
#                 {"messages": {"$size": 0}},
#                 {"status": ContactState.ESTABLISHED}
#             ]
#         }
#     elif contact_type == ContactType.LIKES:
#         match_query = {
#             "$and": [
#                 {"respondent": user_id},
#                 {"messages": {"$size": 0}},
#                 {"status": None},
#                 {"initializer_state": ContactState.ESTABLISHED}
#             ]
#         }
#     elif contact_type == ContactType.DIALOG:
#         match_query = {
#             "$and": [
#                 match_query,
#                 {"status": ContactState.ESTABLISHED},
#                 {"messages": {"$ne": []}}
#             ]
#         }
#
#     pipeline = [
#         {
#             "$match": match_query
#         },
#         {
#             "$addFields": {
#                 "opposite_user": {
#                     "$cond": {
#                         "if": {"$eq": ["$initiator", user_id]},
#                         "then": "$respondent",
#                         "else": "$initiator"
#                     }
#                 }
#             }
#         },
#         {
#             "$lookup": {
#                 "from": "user",
#                 "localField": "opposite_user",
#                 "foreignField": "_id",
#                 "as": "opposite_user"
#             }
#         },
#         {"$unwind": "$opposite_user"},
#         {"$unset": "opposite_user.events"},
#         {
#             "$match": {"opposite_user.is_active": True, "opposite_user.banned": False, },
#         },
#     ]
#
#     result = list(Contact.objects.aggregate(pipeline))
#     return result