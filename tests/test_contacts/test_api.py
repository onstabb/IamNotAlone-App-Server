


def test_get_contact(client, contact_factory):
    created_contact = contact_factory.create(active_dialog=True)
    current_user, target_user = created_contact.initiator, created_contact.respondent
    client.bearer_token = current_user.token

    response = client.get(f"/api/v1/users/me/contacts/{target_user.id}")

    response_data = response.json()
    assert response_data["user"]["id"] == str(target_user.id)
    assert response_data["status"] == created_contact.status.value
