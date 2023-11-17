from datetime import datetime

from users.models import User


def get_candidates(user: User, limit: int = 1) -> list[dict]:
    match_query = {
        "is_active": True,
        "banned": False,
        "_id": {"$ne": user.id},
        "$or":[
            {"profile.gender_preference": {"$eq": user.profile.gender}},
            {"profile.gender_preference": {"$eq": None}}
        ],
        "photo_urls": {"$ne": []}
    }
    if user.profile.gender_preference is not None:
        match_query["profile.gender"] = user.profile.gender_preference


    pipeline = [
        {"$geoNear": {
            "near": user.profile.location.current_geo_json,
            "distanceField": "profile.location.distance",
            "query": match_query,
            "spherical": True,
            }
        },

        {"$lookup":
            {"from": "user_contact",
             "let": {"user_id": "$_id"},
             "pipeline": [
                {"$match":
                    {"$expr":
                        {"$or": [
                              {"$and":
                                  [
                                      {"$eq": ["$initiator", user.id]},
                                      {"$eq": ["$respondent", "$$user_id"]}
                                  ]
                              },
                              {"$and":
                                  [
                                      {"$eq": ["$initiator", "$$user_id"]},
                                      {"$eq": ["$respondent", user.id]}
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
                           {"endDate": "$profile.birthday",

                            "startDate": datetime(
                                user.profile.birthday.year, user.profile.birthday.month, user.profile.birthday.day
                            ),
                            "unit": "year",
                            },
                       },
                 },
            'has_common_events':
                {'$gt': [{'$size': {'$setIntersection': ['$events.participants', [user.id, '$_id']]}}, 1]},
            }
        },

        {'$unset': ['events', 'contacts']},
        {"$sort": {"profile.location.distance": 1, "age_difference": 1, "last_online": 1}, },
        {"$limit": limit},
    ]

    result = list(User.objects.aggregate(pipeline))
    return result