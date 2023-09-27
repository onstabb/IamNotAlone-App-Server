import pytest

from conftest import get_auth_headers
from profiles.enums import Gender
from profiles.schemas import PublicProfileOut


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

    headers = get_auth_headers(main_user)
    response = client.get("/api/v1/contacts/select", headers=headers)


    assert response.status_code == 200
    data = response.json()

    for doc in data:
        candidate = PublicProfileOut(**doc)
        assert profile.gender == candidate.gender_preference or candidate.gender_preference is None
        assert profile.gender_preference == candidate.gender or profile.gender_preference is None
