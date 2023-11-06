from datehelpers import get_aware_datetime_now
from events.models import Event
from models import PydanticObjectId
from profiles.models import Profile


def get_actual_events_in_city(city_id: int) -> list[Event]:
    return list(Event.objects(city_id=city_id, start_at__gt=get_aware_datetime_now()))


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
