import pytest

from factories.generators import generate_random_mobile_number


@pytest.fixture()
def generated_phone_number(factory_random):
    return generate_random_mobile_number(factory_random.randgen)


def test_signup(client, generated_phone_number):
    response = client.post("/api/v1/signup", json={'phone_number': generated_phone_number})
    data: dict = response.json()

    assert response.status_code == 200
    assert data.get("sms_expires_at")



def test_confirm_sms(client, generated_phone_number):
    from authorization.smsservice.baseservice import BaseSmsService

    BaseSmsService.send_sms_verification(generated_phone_number, 'uk')

    code = BaseSmsService.get_code(generated_phone_number)
    prepared_data = {"phone_number": generated_phone_number, "sms_code": code}
    response = client.post("/api/v1/confirm-sms", json=prepared_data)
    data_response = response.json()
    new_password = data_response.get("new_password")

    assert response.status_code == 200
    assert data_response.get("access_token")
    assert new_password

def test_incorrect_login(client, generated_phone_number):
    password = "incorrect"
    response = client.post(
        "/api/v1/login", json={"phone_number": generated_phone_number, "password": password}
    )
    assert response.status_code == 401


def test_login(client, generated_phone_number, user_factory):
    from authorization.password import get_password_hash, build_password
    password = build_password()
    user_factory.create(phone_number=generated_phone_number, password=get_password_hash(password))

    response = client.post(
        "/api/v1/login", json={"phone_number": generated_phone_number, "password": password}
    )
    response_data = response.json()

    assert response.status_code == 200
    assert response_data.get("access_token")


