

def test_get_user(client, user):
    response = client.get(f"/api/v1/users/{user.id}")
    assert response.status_code == 200


def test_get_me(client, authorized_user):
    response = client.get(f"/api/v1/users/me")
    assert response.status_code == 200