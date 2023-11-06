from fastapi import APIRouter, status

from authorization.router import router as auth_router
from contacts.router import router as contact_router
from events.router import router as event_router
from messages.router import router as message_router
from notifications.router import router as notification_router
from profiles.router import router as profile_router


api_router: APIRouter = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router, tags=["Authorization"], prefix="")
api_router.include_router(contact_router, tags=['Contacts'], prefix="/contacts")
api_router.include_router(event_router, tags=["Events"], prefix="/events")
api_router.include_router(message_router, tags=['Messages'], prefix="/messages")
api_router.include_router(notification_router, tags=["Notifications"], prefix="/notifications")
api_router.include_router(profile_router, tags=['Profiles'], prefix='/profiles')


@api_router.get("/health", status_code=status.HTTP_204_NO_CONTENT)
def check_alive():
    return
