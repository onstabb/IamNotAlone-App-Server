from bson import ObjectId
from mongoengine import Q as MQ, DoesNotExist

from contacts.enums import ContactState
from contacts.models import ProfileContact, CONTACT_RESULT_TABLE
from contacts.schemas import ContactStateIn, ContactCreateDataIn
from profiles.models import Profile



def get_contact(contact_id: ObjectId) -> ProfileContact | None:
    return ProfileContact.get_one(id=str(contact_id))


def get_new_established_contacts(profile: Profile, ) -> list[dict]:

    pipeline = [
        # Only established
        {
            "$match": {
                "$or": [{"respondent": profile.id}, {"initiator": profile.id}],
                "status": ContactState.ESTABLISHED
            }
        },

        # No common messages
        {
            "$lookup": {
                "from": "message",
                "let": {
                    "initiatorId": "$initiator",
                    "respondentId": "$respondent"
                },
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$or": [
                                    {
                                        "$and": [
                                            {
                                                "$eq": ["$sender", "$$initiatorId"]
                                            },
                                            {
                                                "$eq": ["$recipient", "$$respondentId"]
                                            }
                                        ]
                                    },
                                    {
                                        "$and": [
                                            {
                                                "$eq": ["$sender", "$$respondentId"]
                                            },
                                            {
                                                "$eq": ["$recipient", "$$initiatorId"]
                                            }
                                        ]
                                    }
                                ]
                            }
                        }
                    }
                ],
                "as": "messages"
            }
        },
        {
            "$match": {"messages": {"$eq": []}}
        },

        # Filter disabled
        {
            "$lookup": {
                "from": "profile",
                "localField": "initiator",
                "foreignField": "_id",
                "as": "initiator"
            }
        },
        {
            "$lookup": {
                "from": "profile",
                "localField": "respondent",
                "foreignField": "_id",
                "as": "respondent"
            }
        },
        {
            "$unwind": "$respondent"
        },
        {
            "$unwind": "$initiator"
        },
        {
            "$match": {
                "initiator.disabled": False,
                "respondent.disabled": False
            }
        },
    ]

    return list(ProfileContact.objects.aggregate(pipeline))


def get_profile_likes(profile: Profile) -> list[dict]:
    pipeline = [
        {
            "$match": {
                "respondent": profile.id,
                "status": None,
                "respondent_state": None,
                "initiator_state": ContactState.ESTABLISHED,
            }
        },

        # Filter disabled profiles
        {
            "$lookup": {
                "from": "profile",
                "localField": "initiator",
                "foreignField": "_id",
                "as": "initiator"
            }
        },
        {
            "$lookup": {
                "from": "profile",
                "localField": "respondent",
                "foreignField": "_id",
                "as": "respondent"
            }
        },
        {
            "$unwind": "$respondent"
        },
        {
            "$unwind": "$initiator"
        },
        {
            "$match": {
                "initiator.disabled": False,
                "respondent.disabled": False
            }
        },
    ]
    return list(ProfileContact.objects.aggregate(pipeline))



def get_contact_by_profile_ids(
        first_profile_id: str | ObjectId, second_profile_id: str | ObjectId
) -> ProfileContact | None:

    query = ((MQ(initiator=first_profile_id) & MQ(respondent=second_profile_id)) |
              (MQ(respondent=first_profile_id) & MQ(initiator=second_profile_id)))
    try:
        contact: ProfileContact = ProfileContact.objects.get(query)
        return contact
    except DoesNotExist:
        return None


def create_contact_by_initiator(
        initiator: 'Profile', respondent: 'Profile', data_in: ContactCreateDataIn,
) -> ProfileContact:
    contact = ProfileContact(
        initiator=initiator, respondent=respondent, initiator_state=data_in.action
    )
    contact.status = get_contact_status(contact.respondent_state, contact.initiator_state)
    contact.save()
    return contact


def update_contact_status(
        contact_state_data: ContactStateIn, profile: Profile, contact: ProfileContact
) -> ProfileContact:

    if contact.initiator == profile:
        contact.initiator_state = contact_state_data.action

    elif contact.respondent == profile:
        contact.respondent_state = contact_state_data.action

    contact.status = get_contact_status(contact.respondent_state, contact.initiator_state)
    contact.save()
    return contact


def get_profile_state(profile: Profile, contact: ProfileContact) -> ContactState | None:
    if profile == contact.initiator:
        return contact.initiator_state
    elif profile == contact.respondent:
        return contact.respondent_state
    else:
        raise ValueError("Given profile must be in this relationship!")


def get_contact_status(state_1: ContactState | None, state_2: ContactState | None) -> ContactState | None:
    enum_list: list[ContactState | None] = [None] + list(ContactState)
    index_1: int = enum_list.index(state_1)
    index_2: int = enum_list.index(state_2)
    return CONTACT_RESULT_TABLE[index_1][index_2]
