__all__ = ("init_db", "close_db")

import typing

import mongoengine

from authorization.models import User
from contacts.models import ProfileContact
from events.models import Event
from geodata.models import City
from profiles.models import Profile


def init_db(**configuration) -> typing.Any:

    Profile.register_delete_rule(City, 'current_city', mongoengine.DO_NOTHING)
    Profile.register_delete_rule(City, 'native_city', mongoengine.DO_NOTHING)
    Profile.register_delete_rule(Event, 'events', mongoengine.DO_NOTHING)
    # Profile.register_delete_rule(ProfileContact, 'initialized_contacts', mongoengine.CASCADE)

    User.register_delete_rule(Profile, "profile", mongoengine.CASCADE)
    Event.register_delete_rule(Profile, 'participants', mongoengine.DO_NOTHING)

    return mongoengine.connect(**configuration)


def close_db() -> None:
    mongoengine.disconnect_all()
