from bson import ObjectId

from datehelpers import get_aware_datetime_now
from events.models import Event
from users.models import User


def get_events_by_city_id(city_id: int, **filters) -> list[Event]:
    if filters.pop("only_future", None):
        filters.update(start_at__gt=get_aware_datetime_now())

    result = Event.objects(city_id=city_id, **filters).exclude("subscribers")
    return list(result)


def get_events_by_user(user: User, *, only_future: bool) -> list[Event]:
    if not only_future:
        return user.events

    return [event for event in user.events if event.start_at < get_aware_datetime_now()]


def accept_subscriber(event: Event, user: User) -> Event:
    if event not in user.events:
        user.events.append(event)

    if user not in event.subscribers:
        event.subscribers.append(user)

    user.save()
    event.save()
    return event


def remove_subscriber(event: Event, user: User) -> Event:
    if event in user.events:
        user.events.remove(event)

    if user in event.subscribers:
        event.subscribers.remove(event)

    user.save()
    event.save()
    return event


def get_event_by_id(event_id: ObjectId | str) -> Event | None:
    return Event.get_one(id=event_id)
