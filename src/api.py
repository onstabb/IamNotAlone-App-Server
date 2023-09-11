from fastapi import APIRouter

from src.authorization.router import router as auth_router
from src.contacts.router import router as contact_router
from src.events.router import router as event_router
from src.files.router import router as file_router
from src.messages.router import router as message_router
from src.profiles.router import router as profile_router

api_router: APIRouter = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(contact_router)
api_router.include_router(event_router)
api_router.include_router(file_router)
api_router.include_router(message_router)
api_router.include_router(profile_router)
