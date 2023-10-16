import mongoengine

from authorization.models import User
from profiles.models import Profile
from profiles.schemas import PrivateProfileIn
from geodata.models import City
from geodata.service import create_city_if_not_exists


def get_active_profile(profile_id: str) -> Profile | None:
    try:
        profile = Profile.get_one(id=str(profile_id), disabled=False)
    except mongoengine.DoesNotExist:
        return None
    return profile


def get_profiles(*ids: str) -> list[Profile]:
    return list(Profile.objects(id__in=ids))


def create_or_update_profile(profile_data: PrivateProfileIn, user: User) -> Profile:
    current_city = create_city_if_not_exists(profile_data.current_city)
    native_city: City | None = None
    if profile_data.native_city:
        native_city = create_city_if_not_exists(profile_data.native_city)

    prepared_data = profile_data.model_dump()
    prepared_data['native_city'] = None if not native_city else native_city.to_dbref()
    prepared_data['current_city'] = current_city.to_dbref()
    prepared_data['photo_urls'] = [photo_url.__str__() for photo_url in prepared_data['photo_urls']]

    if not prepared_data.get("coordinates"):
        prepared_data["coordinates"] = current_city.coordinates

    if user.profile:
        user.profile.update(**prepared_data)
        user.profile.reload()
    else:
        new_profile = Profile(**prepared_data)
        new_profile.save()
        user.profile = new_profile.to_dbref()
        user.save()

    return user.profile
