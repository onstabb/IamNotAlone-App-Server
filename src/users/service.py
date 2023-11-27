from models import PydanticObjectId
from users.enums import UserRole
from users.models import User


def get_user_by_id(user_id: PydanticObjectId | str, **filters) -> User | None:
    return User.get_one(id=user_id, **filters)


def get_active_completed_user_by_id(user_id: PydanticObjectId | str) -> User | None:
    return User.get_one(
        id=user_id, profile__ne=None, is_active=True, banned=False, photo_urls__ne=[], role__nin=UserRole.managers()
    )

