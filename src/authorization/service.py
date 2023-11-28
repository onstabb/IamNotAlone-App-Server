__all__ = ('get_user_by_phone_number', 'create_user', 'update_user_password', "create_admin")

import logging

from authorization import config
from security import hash_password
from users.enums import UserRole
from users.models import User


log = logging.getLogger(__name__)


def get_user_by_phone_number(phone_number: str, **query) -> User | None:
    return User.get_one(phone_number=phone_number, **query)


def create_user(phone_number: str, password: str) -> User:
    new_user: User = User(phone_number=phone_number, password=password)
    new_user.save()
    return new_user


def update_user_password(user: User, password: str) -> User:
    user.password = password
    user.save()
    return user


def create_admin() -> User:
    password = config.ADMIN_PASSWORD
    admin: User = (
        get_user_by_phone_number(config.ADMIN_PHONE_NUMBER) or
        User(
            phone_number=config.ADMIN_PHONE_NUMBER,
            password=hash_password(password),
            is_active=False,
            role=UserRole.ADMIN
        )
    )
    admin.save()

    log.info(f"Initialized Admin({admin.phone_number}, {password}), Token: {admin.token[0]}")
    return admin