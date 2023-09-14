from authorization.models import User
from authorization.password import get_password_hash
from authorization.mobilephonenumber import MobilePhoneNumber



def get_user(phone_number: MobilePhoneNumber) -> User | None:
    return User.get_one(phone_number=phone_number)


def get_user_by_id(user_id: str) -> User | None:
    return User.get_one(id=user_id)


def create_user(phone_number: MobilePhoneNumber, password: str) -> User:
    new_user: User = User(phone_number=phone_number, password=get_password_hash(password))
    new_user.save()
    return new_user


def update_user(user: User) -> User:
    user.save()
    return user


def update_user_password(user: User, password: str) -> User:
    user.password = get_password_hash(password)
    user.save()
    return user