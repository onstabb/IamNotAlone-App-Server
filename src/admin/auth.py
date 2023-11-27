from fastapi import Request, Response


from starlette_admin.auth import AuthProvider, AdminUser
from starlette_admin.exceptions import FormValidationError, LoginFailed

from authorization import service
from authorization.phonenumber import validate_mobile_phone_number
from users.enums import UserRole
from users.models import User

users = {
    "admin": {
        "name": "Admin",
        "avatar": "admin.png",
        "company_logo_url": "admin.png",
        "roles": ["read", "create", "edit", "delete", "action_make_published"],
    },
    "johndoe": {
        "name": "John Doe",
        "avatar": None, # user avatar is optional
        "roles": ["read", "create", "edit", "action_make_published"],
    },
    "viewer": {"name": "Viewer", "avatar": "guest.png", "roles": ["read"]},
}


class AdminCredentialsProvider(AuthProvider):

    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request,
        response: Response,
    ) -> Response:
        try:
            phone_number = validate_mobile_phone_number(username)
        except ValueError:
            raise FormValidationError({"username": "Incorrect format"})

        user: User | None = service.get_user_by_phone_number(phone_number)
        if not user or not user.check_password(password):
            raise LoginFailed("Invalid phone number or password")

        if user.role not in UserRole.managers():
            raise LoginFailed("Permission denied")

        if user.banned:
            raise LoginFailed("This user is banned")

        request.session.update(phone_number=user.phone_number)
        return response


    async def is_authenticated(self, request: Request) -> bool:
        phone_number: str = request.session.get("phone_number")
        if not phone_number:
            return False

        user: User | None = service.get_user_by_phone_number(phone_number)
        if not user or user.banned:
            return False

        request.state.user = user
        return True

    def get_admin_user(self, request: Request) -> AdminUser:
        user: User = request.state.user
        photo_url = user.photo_urls[0] if len(user.photo_urls) > 0 else None
        return AdminUser(username=user.phone_number, photo_url=photo_url)

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response
