from mongoengine import Q as MQ

from contacts.enums import ContactState
from messages.models import Message
from models import PydanticObjectId
from profiles.models import Profile


def create_message(sender: Profile, recipient: Profile, content_text: str) -> Message:
    message = Message(sender=sender, recipient=recipient, content_text=content_text)
    message.save()
    return message


def get_chat(
        first_profile: Profile | str | PydanticObjectId, second_profile: Profile | str | PydanticObjectId
) -> list[Message]:
    query = ((MQ(sender=first_profile) & MQ(recipient=second_profile)) |
             (MQ(recipient=first_profile) & MQ(sender=second_profile)))
    return list(Message.objects(query))


def get_messages_count(sender: Profile | str, recipient: Profile | str) -> int:
    return len(Message.objects(sender=sender, recipient=recipient))


def get_dialogs(profile: Profile | PydanticObjectId) -> list[dict]:
    profile_id: PydanticObjectId = profile.id if isinstance(profile, Profile) else profile
    pipeline = [
        {
            "$lookup": {
                "from": "profile_contact",
                "let": {
                    "senderId": "$sender",
                    "recipientId": "$recipient"
                },
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {
                                        "$or": [
                                            {
                                                "$and": [
                                                    {
                                                        "$eq": ["$initiator", "$$senderId"]
                                                    },
                                                    {
                                                        "$eq": ["$respondent", "$$recipientId"]
                                                    }
                                                ]
                                            },
                                            {
                                                "$and": [
                                                    {
                                                        "$eq": ["$initiator", "$$recipientId"]
                                                    },
                                                    {
                                                        "$eq": ["$respondent", "$$senderId"]
                                                    }
                                                ]
                                            }
                                        ]
                                    },
                                    {
                                        "$eq": ["$status", ContactState.ESTABLISHED]
                                    }
                                ]
                            }
                        }
                    }
                ],
                "as": "contact"
            }
        },
        {
            "$match": {
                "$or": [
                    {"sender": profile_id},
                    {"recipient": profile_id}
                ],
                "contact": {"$ne": []}
            }
        },
        {
            "$unwind": "$contact"
        },
        {
            "$set": {
                "created_at": {
                    "$toDate": "$_id"
                }
            }
        },
        {
            "$sort": {"_id": -1}
        },
        {
            "$lookup": {
                "from": "profile",
                "localField": "sender",
                "foreignField": "_id",
                "as": "sender_profile"
            }
        },
        {
            "$unwind": "$sender_profile"
        },
        {
            "$lookup": {
                "from": "profile",
                "localField": "recipient",
                "foreignField": "_id",
                "as": "recipient_profile"
            }
        },
        {
            "$unwind": "$recipient_profile"
        },
        {
            "$group": {
                "_id": {
                    "$cond": {
                        "if": {"$eq": ["$sender", profile_id]},
                        "then": "$recipient",
                        "else": "$sender"
                    }
                },
                "lastMessage": {"$first": "$$ROOT"},
                "sender_profile": {
                    "$first": {
                        "_id": "$sender_profile._id",
                        "name": "$sender_profile.name",
                        "photo": {"$arrayElemAt": ["$sender_profile.photo_urls", 0]}
                    }
                },
                "recipient_profile": {
                    "$first": {
                        "_id": "$recipient_profile._id",
                        "name": "$recipient_profile.name",
                        "photo": {"$arrayElemAt": ["$recipient_profile.photo_urls", 0]}
                    }
                }
            }
        },
        {
            "$project": {
                "_id": "$lastMessage._id",
                "sender": "$sender_profile",
                "recipient": "$recipient_profile",
                "content_text": "$lastMessage.content_text",
                "created_at": "$lastMessage.created_at"
            }
        }
    ]

    return list(Message.objects.aggregate(pipeline))
