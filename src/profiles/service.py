from datetime import datetime

import mongoengine

from authorization.models import User
from profiles.models import Profile
from profiles.schemas import PrivateProfileIn


def get_active_profile(profile_id: str) -> Profile | None:
    try:
        profile = Profile.get_one(id=str(profile_id), disabled=False)
    except mongoengine.DoesNotExist:
        return None
    return profile


def get_profiles(*ids: str) -> list[Profile]:
    return list(Profile.objects(id__in=ids))


def _set_location(profile: Profile, profile_data: PrivateProfileIn) -> Profile:
    profile.location.coordinates = profile_data.coordinates
    profile.location.city_coordinates = profile_data.current_city.coordinates
    if not profile.location.coordinates:
        profile.location.coordinates = profile_data.current_city.coordinates
    return profile


def create_profile(profile_data: PrivateProfileIn, user: User) -> Profile:
    prepared_data = profile_data.model_dump(exclude_unset=True, by_alias=True)
    new_profile = Profile(**prepared_data)
    _set_location(new_profile, profile_data)
    new_profile.save()
    user.profile = new_profile.to_dbref()
    user.save()
    return user.profile


def update_profile(profile_data: PrivateProfileIn, profile: Profile) -> Profile:
    prepared_data = profile_data.model_dump(exclude_unset=True, by_alias=True)
    _set_location(profile, profile_data)
    profile.update(**prepared_data)
    profile.reload()
    return profile



def get_candidates(profile: 'Profile', limit: int = 1) -> list[dict]:

    match_query = {
        "disabled": False,
        "_id": {"$ne": profile.id},
        "$or":[{"gender_preference": {"$eq": profile.gender}}, {"gender_preference": {"$eq": None}}],
        "photo_urls": {"$ne": []}
    }

    if profile.gender_preference is not None:
        match_query["gender"] = profile.gender_preference

    pipeline = [
        {"$geoNear": {
            "near": profile.location.coordinates,
            "distanceField": "location.distance",
            "query": match_query,
            "spherical": True,
            "key": "location.city_coordinates",
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
                                      {"$eq": ["$initiator", profile.id]},
                                      {"$eq": ["$respondent", "$$profile_id"]}
                                  ]
                              },
                              {"$and":
                                  [
                                      {"$eq": ["$initiator", "$$profile_id"]},
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
        {"$sort": {"location.distance": 1, "age_difference": 1, "last_online": 1}, },
        {"$limit": limit},
    ]

    result = list(Profile.objects.aggregate(pipeline))
    return result
