

def test_create_profile(client, user_factory, userprofile_factory):
    user = user_factory.create(profile=None, is_active=True)
    client.bearer_token = user.token
    request_data = userprofile_factory.build_json_dict()

    response = client.put("/api/v1/users/me/profile", json=request_data)
    response_data: dict = response.json()

    assert response.status_code == 201
    assert response_data.get("profile")


def test_edit_profile(client, authorized_user, userprofile_factory):
    request_data = userprofile_factory.build_json_dict()

    response = client.put("/api/v1/users/me/profile", json=request_data,)
    response_data: dict = response.json()

    assert response.status_code == 200
    for key in request_data:
        assert request_data[key] == response_data["profile"].get(key)

