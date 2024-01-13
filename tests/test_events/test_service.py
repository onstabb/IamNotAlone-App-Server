import datehelpers
from events import service


def test_get_event_by_id(event_factory):
    event = event_factory.create()
    found_event = service.get_event_by_id(event.id)
    assert event == found_event


def test_get_events_by_city_id(event_factory):
    event = event_factory.create(future=True)
    found_events = service.get_events_by_city_id(event.city_id, only_future=True)
    assert event in found_events


def test_accept_subscriber(event_factory, user):
    event = event_factory.create(subscribers=[])

    service.accept_subscriber(event, user)

    assert user in event.subscribers
    assert event in user.events