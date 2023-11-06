from fastapi import APIRouter, Depends, HTTPException, status

from datehelpers import get_aware_datetime_now
from events import service
from events.schemas import EventOut
from profiles.dependencies import CurrentActiveProfileByToken

router = APIRouter()


@router.get("/", response_model=list[EventOut],)
def get_actual_events(city_id: int):
    return service.get_actual_events_in_city(city_id)


@router.get("/my", response_model=list[EventOut])
def get_my_actual_events(profile: CurrentActiveProfileByToken):
    return [event for event in profile.events if event.start_at < get_aware_datetime_now()]


@router.patch("/{event_id}", response_model=EventOut)
def accept_subscriber(event_id: str, profile: CurrentActiveProfileByToken):
    event = service.get_event(event_id)

    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    if profile in event.subscribers:
        return event

    return service.accept_subscriber(event, profile)

