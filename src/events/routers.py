from fastapi import APIRouter, HTTPException, status

from datehelpers import get_aware_datetime_now
from events import service
from events.schemas import EventOut
from models import PydanticObjectId
from users.dependencies import CurrentActiveCompletedUser


router = APIRouter()
user_router = APIRouter()


@router.get("", response_model=list[EventOut])
def get_actual_events(city_id: int):
    return service.get_actual_events_in_city(city_id)


@router.patch("/{event_id}", response_model=EventOut)
def accept_subscriber(event_id: PydanticObjectId, current_user: CurrentActiveCompletedUser):
    event = service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    if current_user in event.subscribers:
        return event

    return service.accept_subscriber(event, current_user)


@user_router.get("", response_model=list[EventOut])
def get_my_actual_events(current_user: CurrentActiveCompletedUser):
    return [event for event in current_user.events if event.start_at < get_aware_datetime_now()]
