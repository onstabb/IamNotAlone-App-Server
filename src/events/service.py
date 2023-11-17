from datehelpers import get_aware_datetime_now
from events.models import Event
from models import PydanticObjectId
from users.models import User


def get_actual_events_in_city(city_id: int) -> list[Event]:
    result = Event.objects(city_id=city_id, start_at__gt=get_aware_datetime_now())
    return list(result)


def accept_subscriber(event: Event, user: User) -> Event:
    if event not in user.events:
        user.events.append(event)

    if user not in event.subscribers:
        event.subscribers.append(user)

    user.save()
    event.save()
    return event


def get_event(event_id: PydanticObjectId | str) -> Event | None:
    return Event.get_one(id=event_id)
