from fastapi import APIRouter, status

from authorization.routers import router as auth_router
from candidates.routers import router as candidates_router
from contacts.routers import router as contact_router
from events.routers import router as event_router
from events.routers import user_router as user_events_router
from notifications.routers import router as notifications_router
from photos.routers import router as photos_router
from reports.routers import router as reports_router
from userprofile.routers import router as profile_router
from users.routers import router as users_router


api_router: APIRouter = APIRouter(prefix="/api/v1")
api_router.include_router(users_router, tags=['Users'], prefix='/users')
api_router.include_router(auth_router, tags=["Authorization"], prefix="")
api_router.include_router(event_router, tags=["Events"], prefix="/events")
api_router.include_router(reports_router, tags=["Reports"], prefix="/reports")

authenticated_router: APIRouter = APIRouter(prefix="/users/me", tags=["Users"])
authenticated_router.include_router(profile_router, tags=["Profile"], prefix="/profile")
authenticated_router.include_router(photos_router, tags=["Photos"], prefix="/photos")
authenticated_router.include_router(candidates_router, tags=["Candidates"], prefix="/candidates")
authenticated_router.include_router(contact_router, tags=["Contacts"], prefix="/contacts")
authenticated_router.include_router(user_events_router, tags=["Events"], prefix="/events")
authenticated_router.include_router(notifications_router, tags=["Notifications"], prefix="/notifications")

api_router.include_router(authenticated_router)


@api_router.get("/health", status_code=status.HTTP_204_NO_CONTENT, include_in_schema=False)
def check_alive():
    return
