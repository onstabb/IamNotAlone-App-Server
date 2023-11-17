__all__ = ("init_db", "close_db")

import mongoengine
from pymongo import MongoClient

from contacts.models import Contact
from events.models import Event
from users.models import User



def init_db(**configuration) -> MongoClient:

    Contact.register_delete_rule(User, 'initiator', mongoengine.DENY)
    Contact.register_delete_rule(User, 'respondent', mongoengine.DENY)


    Event.register_delete_rule(User, 'subscribers', mongoengine.PULL)
    User.register_delete_rule(Event, 'events', mongoengine.PULL)

    return mongoengine.connect(**configuration)


def close_db() -> None:
    mongoengine.disconnect_all()
