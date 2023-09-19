from datetime import datetime

from mongoengine import Q as MQ, DoesNotExist

from contacts import config
from contacts.enums import ContactState
from contacts.models import ProfileContact, CONTACT_RESULT_TABLE
from contacts.schemas import RateIn
from profiles.enums import Gender
from profiles.models import Profile


def get_contact(first_profile: 'Profile', second_profile: 'Profile',) -> ProfileContact | None:
    return get_contact_by_profile_ids(first_profile.id, second_profile.id)


def get_contact_by_profile_ids(first_profile_id: str, second_profile_id: str) -> ProfileContact | None:

    query = ((MQ(initializer=first_profile_id) & MQ(respondent=second_profile_id)) |
              (MQ(respondent=first_profile_id) & MQ(initializer=second_profile_id)))
    try:
        contact: ProfileContact = ProfileContact.objects.get(query)
        return contact
    except DoesNotExist:
        return None


def create_contact(initializer: 'Profile', respondent: 'Profile') -> ProfileContact:
    contact = ProfileContact(initializer=initializer, respondent=respondent)
    contact.save()
    return contact


def update_rate(rate_in: RateIn, contact: ProfileContact, by_initializer: bool) -> ProfileContact:

    if by_initializer:
        contact.initializer_state = rate_in.contact
    else:
        contact.respondent_state = rate_in.contact

    contact.status = get_contact_status(contact.respondent_state, contact.initializer_state)
    contact.save()
    return contact


def get_profile_state(profile: Profile, contact: ProfileContact) -> ContactState:

    if profile == contact.initializer:
        return contact.initializer_state
    elif profile == contact.respondent:
        return contact.respondent_state
    else:
        raise ValueError("Given profile must be in this relationship!")


def get_contact_status(state_1: ContactState, state_2: ContactState) -> ContactState:
    enum_list: list[ContactState] = list(ContactState)
    index_1: int = enum_list.index(state_1)
    index_2: int = enum_list.index(state_2)
    return CONTACT_RESULT_TABLE[index_1][index_2]


def get_candidates(profile: 'Profile', maximum: int = config.CANDIDATES_LIMIT) -> list[dict]:

    match_query = {
        "disabled": False,
        "_id": {"$ne": profile.id},
        "$or":[{"gender_preference": {"$eq": profile.gender}}, {"gender_preference": {"$eq": None}}]

    }

    if profile.gender_preference is not None:
        match_query["gender"] = profile.gender_preference

    pipeline = [
        {"$geoNear": {
            "near": profile.coordinates,
            "distanceField": "distance",
            "query": match_query,
            "spherical": True,
            }
        },
        # {"$match": match_query},

        {"$lookup":
            {"from": "profile_contact",
             "let": {"profile_id": "$_id"},
             "pipeline": [
                {"$match":
                    {"$expr":
                        {"$or": [
                              {"$and":
                                  [
                                      {"$eq": ["$initializer", profile.id]},
                                      {"$eq": ["$respondent", "$$profile_id"]}
                                  ]
                              },
                              {"$and":
                                  [
                                      {"$eq": ["$initializer", "$$profile_id"]},
                                      {"$eq": ["$respondent", profile.id]}
                                  ]
                              },
                          ]
                        },

                    }
                }
             ],
             "as": "contacts"
            }
        },
        {"$match": {"contacts": {"$eq": []}}},

        {"$lookup":
             {"from": "city",
              "let": {"location": "$coordinates", "current_city_id": "$current_city", },
              "pipeline": [
                  {"$geoNear":
                       {"near": profile.current_city.coordinates,
                        "distanceField": "distance",
                        "spherical": True,
                        },
                  },
                  {"$match": {"$expr": {"$eq": ["$_id", "$$current_city_id"]}},}
              ],
              "as": "current_city_doc",
              },
        },
        {"$unwind": "$current_city_doc"},

        {'$lookup':
            {
                'from': 'event',
                'localField': '_id',
                'foreignField': 'participants',
                'as': 'events'
            }
        },

        {"$addFields":
            {"age_difference":
                 {"$abs":
                      {"$dateDiff":
                           {"endDate": "$birthday",
                            "startDate": datetime(profile.birthday.year, profile.birthday.month, profile.birthday.day),
                            "unit": "year",
                            },
                       },
                 },
            'has_common_events':
                {'$gt': [{'$size': {'$setIntersection': ['$events.participants', [profile.id, '$_id']]}}, 1]},
            }
        },

        {'$unset': ['events', 'contacts']},
        {"$sort": {"current_city_doc.distance": 1, "age_difference": 1, "last_online": 1}, },
        {"$limit": maximum},
    ]

    result = list(Profile.objects.aggregate(pipeline))
    return result
