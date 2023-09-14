from mongoengine import Q as MQ

from messages.enums import MessageType
from messages.models import Message
from models import PydanticObjectId
from profiles.models import Profile


def create_message(sender: Profile, recipient: Profile, message_type: MessageType, content_text: str | None) -> Message:

    message = Message(sender=sender, recipient=recipient, message_type=message_type, content_text=content_text)
    message.save()
    return message


def get_chat(
        first_profile: Profile | str,
        second_profile: Profile | str,
        message_type: None | MessageType,
) -> list[Message]:

    query = ((MQ(sender=first_profile) & MQ(recipient=second_profile)) |
             (MQ(recipient=first_profile) & MQ(sender=second_profile)))

    if message_type:
        query &= MQ(message_type=message_type)

    return list(Message.objects(query))



def get_messages_count(sender: Profile | str, recipient: Profile | str, message_type: MessageType) -> int:

    return len(Message.objects(message_type=message_type, sender=sender, recipient=recipient))


def get_message_by_id(message_id: str, recipient: Profile | None = None) -> Message | None:
    query = {"id": message_id}
    if recipient:
        query.update(recipient=recipient)

    return Message.get_one(**query)

def set_message_as_delivered(message: Message) -> Message:

    if message.delivered:
        return message

    message.delivered = True
    message.save()
    return message


def set_message_as_delivered_by_id(message_id: str | PydanticObjectId, recipient_id: str | PydanticObjectId) -> None:
    message = get_message_by_id(message_id)

    if not message:
        return

    if recipient_id != message.recipient.id:
        return

    set_message_as_delivered(message)


def get_dialogs(profile: Profile) -> list[dict]:

    pipeline = [
        {
            "$match": {
                "$or": [
                    {"$and": [{"recipient": profile.id}, {"message_type": MessageType.LIKE.value}]},

                    {"$and": [
                        {"$or": [{"recipient": profile.id}, {"sender": profile.id}]},
                        {"message_type": {"$in":  [MessageType.MESSAGE.value, MessageType.CONTACT_ESTABLISHED.value]}}
                        ]
                    },
                ]
            }
        },
        {"$sort": {"_id": -1}},
        {
            "$group": {
                "_id": {
                    "$cond": [
                        {"$eq": ["$recipient", profile.id]},
                        "$sender",
                        "$recipient"
                    ]
                },
                "latest_message": {
                    "$first": "$$ROOT"
                }
            }
        },

        {
            "$lookup": {
                "from": "profile",
                "localField": "_id",
                "foreignField": "_id",
                "as": "profile"
            }
        },

        {"$unwind": "$profile"},

        {
            "$set": {
                "profile_name": "$profile.name",
                "profile_main_photo_url": {"$arrayElemAt": ["$profile.photo_urls", 0]}
            }
        },
        {"$unset": "profile"}

    ]
    return list(Message.objects.aggregate(pipeline))