from fastapi import APIRouter, Depends, HTTPException, status

from datehelpers import get_aware_datetime_now
from events import service
from events.schemas import EventOut
from profiles import dependencies as profile_dependencies
from profiles.models import Profile

router = APIRouter(tags=["Events"], prefix="/events")


@router.get("/", response_model=list[EventOut], dependencies=[Depends(profile_dependencies.get_active_profile)])
def get_actual_events(city_id: str):
    return service.get_actual_events_in_city(city_id)


@router.get("/my", response_model=list[EventOut])
def get_my_actual_events(profile: Profile = Depends(profile_dependencies.get_active_profile)):
    return [event for event in profile.events if event.start_at < get_aware_datetime_now()]


@router.patch("/{event_id}", response_model=EventOut)
def accept_subscriber(event_id: str, profile: Profile = Depends(profile_dependencies.get_active_profile)):
    event = service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    if profile in event.subscribers:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Already in participants of the event")

    return service.accept_subscriber(event, profile)

