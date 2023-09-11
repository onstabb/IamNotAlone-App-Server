from datetime import datetime

from pytz import utc

from src.events.models import Event
from src.geodata.models import City
from src.models import PydanticObjectId
from src.profiles.models import Profile


def get_actual_events_in_city(city_id: str | City) -> list[Event]:
    return list(Event.objects(city=city_id, start_at=datetime.now(utc)))


def accept_subscriber(event: Event, profile: Profile) -> Event:
    if event not in profile.events:
        profile.events.append(event)

    if profile not in event.subscribers:
        event.subscribers.append(profile)

    profile.save()
    event.save()
    return event


def get_event(event_id: str | PydanticObjectId) -> Event | None:
    return Event.get_one(id=str(event_id))
