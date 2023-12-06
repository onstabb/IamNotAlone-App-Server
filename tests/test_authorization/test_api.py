from authorization.smsservice.baseservice import BaseSmsService
from security import generate_password, hash_password


def test_signup(client, user_factory):
    user = user_factory.build()

    response = client.post("/api/v1/signup", json={'phone_number': user.phone_number})
    data: dict = response.json()

    assert response.status_code == 200
    assert data.get("sms_expires_at")


def test_confirm_sms(client, user_factory):
    user = user_factory.build()
    BaseSmsService.send_sms_verification(user.phone_number, 'uk')
    code = BaseSmsService.get_code(user.phone_number)

    response = client.post("/api/v1/confirm-sms", json={"phone_number": user.phone_number, "sms_code": code})

    data_response = response.json()
    new_password = data_response.get("new_password")

    assert response.status_code == 200
    assert data_response.get("access_token")
    assert new_password


def test_login_incorrect(client, user_factory):
    user = user_factory.build(password="incorrect")

    response = client.post(
        "/api/v1/login", json={"phone_number": user.phone_number, "password": user.password}
    )
    assert response.status_code == 401


def test_login(client, user_factory):
    password = generate_password()
    user = user_factory.create(password=hash_password(password))

    response = client.post(
        "/api/v1/login", json={"phone_number": user.phone_number, "password": password}
    )
    response_data = response.json()

    assert response.status_code == 200
    assert response_data.get("access_token")


