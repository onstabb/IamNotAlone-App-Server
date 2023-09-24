from fastapi import Depends, HTTPException, status

from authorization.dependencies import get_unbanned_user
from authorization.models import User
from datehelpers import get_aware_datetime_now
from profiles.models import Profile
from models import PydanticObjectId
from profiles import service


def get_user_profile(user: User = Depends(get_unbanned_user)) -> Profile:

    if not user.profile:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Filled profile required")

    return user.profile


def get_active_profile(profile: Profile = Depends(get_user_profile)) -> Profile:
    if profile.disabled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Profile is disabled")

    profile.last_online = get_aware_datetime_now()
    profile.save()
    return profile


def get_active_profile_by_id(profile_id: PydanticObjectId):

    if isinstance(profile_id, PydanticObjectId):
        profile_id = profile_id.__str__()

    profile = service.get_active_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Profile with id `{profile_id}` not found")
    return profile
