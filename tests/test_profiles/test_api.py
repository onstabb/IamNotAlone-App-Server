from datetime import date

import pytest

from profiles.enums import ResidencePlan, ResidenceLength, Gender


@pytest.fixture(scope="module")
def data(user_image_url):
    yield {
        "name": "Mark",
        "birthday": date(2000, 3, 12).isoformat(),
        "description": "I like cats, sushi and films.",
        "residence_length": ResidenceLength.SOMETIME.value,
        "residence_plan": ResidencePlan.STAY.value,
        "gender_preference": None,
        "gender": Gender.MALE.value,
        "current_city_id": 3081368,
        "photo_urls": [user_image_url]
    }


def test_error_get_my_profile(client, authorization_user_only):
    response = client.get("/api/v1/profiles/me")
    assert response.status_code == 401


def test_create_profile(client, authorization_user_only, data):
    response = client.put("/api/v1/profiles/me", json=data, headers=authorization_user_only)
    response_data: dict = response.json()

    assert response.status_code == 201
    assert response_data.get("name")


@pytest.mark.parametrize(
    "new_data",
    [
        {"name": "Markus", "description": "...", "residence_length": ResidenceLength.RECENTLY.value},
    ]
)
def test_edit_profile(client, authorization_user_only, data, new_data):
    data.update(new_data)

    response = client.put("/api/v1/profiles/me", json=data, headers=authorization_user_only)

    response_data: dict = response.json()
    assert response.status_code == 200
    for key in data:
        assert data[key] == response_data.get(key)
