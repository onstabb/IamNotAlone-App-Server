from fastapi import APIRouter, HTTPException, status, Query


from events import service
from events.schemas import EventOut
from models import PydanticObjectId
from users.dependencies import CurrentActiveCompletedUser


router = APIRouter()
user_router = APIRouter()


@router.get("", response_model=list[EventOut])
def get_events(city_id: int = Query(alias="cityId"), only_future: bool = Query(alias="onlyFuture", default=True)):
    return service.get_events_by_city_id(city_id, only_future=only_future)


@router.patch("/{event_id}", response_model=EventOut)
def accept_subscriber(event_id: PydanticObjectId, current_user: CurrentActiveCompletedUser):
    event = service.get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    if current_user in event.subscribers:
        return event

    return service.accept_subscriber(event, current_user)


@user_router.get("", response_model=list[EventOut])
def get_my_actual_events(
        current_user: CurrentActiveCompletedUser,
        only_future: bool = Query(alias="onlyFuture", default=True)
):
    return service.get_events_by_user(current_user, only_future=only_future)


