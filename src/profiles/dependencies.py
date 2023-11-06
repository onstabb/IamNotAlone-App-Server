# "Current profile" - profile from auth token, "Target profile" - profile from query/path/body with profile_id,

from typing import Annotated

from fastapi import Depends, HTTPException, status

from authorization.dependencies import get_unbanned_user
from authorization.models import User
from files import service
from profiles.models import Profile
from models import PydanticObjectId, ProfileIdQuery
from profiles import service


def get_current_user_profile(user: User = Depends(get_unbanned_user)) -> Profile:
    if not user.profile:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Completed profile is required")
    return user.profile


def get_current_completed_profile(profile: Profile = Depends(get_current_user_profile)) -> Profile:
    if not profile.photo_urls:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Completed profile is required")
    return profile


# Current, Completed and Active
def get_current_active_profile(profile: Profile = Depends(get_current_completed_profile)) -> Profile:
    if profile.disabled:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Profile is disabled")
    # profile.last_online = get_aware_datetime_now()
    # profile.save()
    return profile


# Target, Completed and Active
def get_active_target_profile(profile_id: PydanticObjectId) -> Profile:
    profile = service.get_active_profile(str(profile_id))
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Profile with id `{profile_id}` not found")
    return profile


# Current or Target, Completed and Active / Uncompleted or Disabled
def get_target_active_or_current_profile(
        profile_id: ProfileIdQuery, current_profile: Profile = Depends(get_current_user_profile)
) -> Profile:
    if profile_id in ('my', current_profile.id):
        return current_profile
    return get_active_target_profile(profile_id)


# Current == Target, Uncompleted or Disabled
def get_current_target_profile(
        profile_id: ProfileIdQuery, current_profile: Profile = Depends(get_current_user_profile),
) -> Profile:
    if profile_id not in ('my', current_profile.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="")
    return current_profile


# Current == Target, Completed and Active
def get_current_target_active_profile(current_profile: Profile = Depends(get_current_target_profile)) -> Profile:
    return get_current_active_profile(current_profile)



CurrentProfileByToken = Annotated[Profile, Depends(get_current_user_profile)]
CurrentActiveProfileByToken = Annotated[Profile, Depends(get_current_active_profile)]
ActiveTargetProfileById = Annotated[Profile, Depends(get_active_target_profile)]
CurrentOrActiveTargetProfile = Annotated[Profile, Depends(get_target_active_or_current_profile)]
CurrentTargetProfile = Annotated[Profile, Depends(get_current_target_profile)]
CurrentTargetActiveProfile = Annotated[Profile, Depends(get_current_target_active_profile)]