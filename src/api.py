from fastapi import APIRouter

from authorization.router import router as auth_router
from contacts.router import router as contact_router
from events.router import router as event_router
from files.router import router as file_router
from messages.router import router as message_router
from profiles.router import router as profile_router

api_router: APIRouter = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(contact_router)
api_router.include_router(event_router)
api_router.include_router(file_router)
api_router.include_router(message_router)
api_router.include_router(profile_router)
