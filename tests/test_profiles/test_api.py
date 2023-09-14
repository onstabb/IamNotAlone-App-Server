from datetime import date

import pytest


@pytest.fixture(scope="module")
def data(user_image_url):
    yield {
        "name": "Mark",
        "birthday": date(2000, 3, 12).isoformat(),
        "description": "I like cats, sushi and films.",
        "residence_length": "sometime",
        "residence_plan": "stay",
        "gender_preference": "any",
        "gender": "male",
        "current_city_id": 3081368,
        "photo_urls": [user_image_url]
    }



def test_get_my_profile_error(client, authorization_user_only):
    response = client.get("/api/v1/profiles/me")
    assert response.status_code == 403


def test_create_profile(client, authorization_user_only, data):

    response = client.post("/api/v1/profiles/me", json=data, headers=authorization_user_only)
    response_data: dict = response.json()

    assert response.status_code == 200
    assert response_data.get("name")




