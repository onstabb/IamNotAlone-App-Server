from datetime import date
from tempfile import NamedTemporaryFile

import pytest

from conftest import get_auth_headers
from profiles.enums import ResidencePlan, ResidenceLength, Gender
from profiles.schemas import PublicProfileOut
from test_profiles.conftest import get_image_path


@pytest.fixture(scope="module")
def profile_data():
    return {
        "name": "Mark",
        "birthday": date(2000, 3, 12).isoformat(),
        "description": "I like cats, sushi and films.",
        "residence_length": ResidenceLength.SOMETIME.value,
        "residence_plan": ResidencePlan.STAY.value,
        "gender_preference": None,
        "gender": Gender.MALE.value,
        "current_city_id": 3081368,
    }


def test_error_get_my_profile(client, auth_headers_user_without_profile):
    response = client.get("/api/v1/profiles/my")
    assert response.status_code == 401


def test_create_profile(client, auth_headers_user_without_profile, profile_data):
    response = client.post("/api/v1/profiles", json=profile_data, headers=auth_headers_user_without_profile)
    response_data: dict = response.json()
    assert response.status_code == 201
    assert response_data.get("name")


@pytest.mark.parametrize(
    "new_data",
    [
        {"name": "Markus", "description": "...", "residence_length": ResidenceLength.RECENTLY.value},
    ]
)
def test_edit_profile(client, auth_headers_user_without_profile, profile_data, new_data):
    profile_data.update(new_data)
    response = client.post("/api/v1/profiles", json=profile_data, headers=auth_headers_user_without_profile)
    response_data: dict = response.json()
    assert response.status_code == 200
    for key in profile_data:
        assert profile_data[key] == response_data.get(key)


def test_upload_profile_photo(client, auth_headers_user_without_profile):
    data = {"photos": open(get_image_path("Test1.jpg"), "rb",)}
    response = client.post("/api/v1/profiles/my/photos", files=data, headers=auth_headers_user_without_profile)

    assert response.status_code == 201

    response_data = response.json()
    assert response_data.get("photo_urls")


def test_upload_profile_corrupted_photo(client, auth_headers_user_without_profile):
    temp_file = NamedTemporaryFile(suffix=".jpg", mode="a+b")
    with open(get_image_path("Test1.jpg"), "rb") as real_file:
        temp_file.write( b'321mdmdmdam-m0m99889h9b98bb09j0nmmmvvbbnn' + real_file.read())

    data = {"photo": temp_file}
    response = client.put("/api/v1/profiles/my/photos/0", files=data, headers=auth_headers_user_without_profile)
    assert response.status_code == 406



@pytest.mark.parametrize(
    "gender_preference,gender, candidate_gender_preference, candidate_gender",
    [
        (Gender.FEMALE, Gender.MALE, Gender.MALE, Gender.FEMALE),
        (None, Gender.FEMALE, None, Gender.MALE),
        (None, Gender.MALE, Gender.MALE, Gender.MALE),
        (Gender.FEMALE, Gender.FEMALE, None, Gender.FEMALE)
    ]
)
def test_success_get_candidates_by_gender_preferences(
        client, user_factory, gender, gender_preference, candidate_gender_preference, candidate_gender
):

    """    This test tests gender preference for both the candidate and the seeker.   """
    user_factory.insert_many(5)
    user_factory.create_batch(
        1,
        profile__disabled=False,
        profile__gender=candidate_gender,
        profile__gender_preference=candidate_gender_preference,
    )

    main_user = user_factory.create(
        profile__gender_preference=gender_preference,
        profile__gender=gender,
        profile__disabled=False,
    )
    profile = main_user.profile

    response = client.get("/api/v1/profiles/my/candidates", headers=get_auth_headers(main_user))


    assert response.status_code == 200
    data = response.json()

    for doc in data:
        candidate = PublicProfileOut(**doc)
        assert profile.gender == candidate.gender_preference or candidate.gender_preference is None
        assert profile.gender_preference == candidate.gender or profile.gender_preference is None
