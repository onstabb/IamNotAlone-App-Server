__all__ = ('get_user_by_phone_number', 'create_user', 'update_user_password')

from users.models import User


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
