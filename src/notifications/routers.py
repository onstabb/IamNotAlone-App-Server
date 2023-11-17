from fastapi import APIRouter, Request, status
from sse_starlette import EventSourceResponse

from notifications.manager import notification_manager
from users.dependencies import CurrentActiveCompletedUser


router = APIRouter()


@router.get(
    "",
    response_class=EventSourceResponse,
    responses={
        status.HTTP_200_OK: {"content": {"text/event-stream": {}}},
    }
)
async def receive_notifications(request: Request, current_user: CurrentActiveCompletedUser):
    return EventSourceResponse(notification_manager.retrieve_events(request, str(current_user.id)),)
