from userprofile.models import UserProfile
from userprofile.schemas import PrivateUserProfileIn
from users.models import User


def create_user_profile(user: User, profile_data: PrivateUserProfileIn) -> User:
    user.profile = UserProfile(**profile_data.model_dump(exclude_unset=True, by_alias=True))
    user.save()
    return user


def update_user_profile(user: User, profile_data: PrivateUserProfileIn) -> User:
    return create_user_profile(user, profile_data)
