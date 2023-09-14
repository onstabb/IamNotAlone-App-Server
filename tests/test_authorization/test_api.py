import pytest

from src.authorization.smsservice.baseservice import BaseSmsService
from tests.factories.generators import generate_random_mobile_number


@pytest.fixture(scope="module")
def generated_phone_number():
    return generate_random_mobile_number()


def test_signup(client, generated_phone_number):
    response = client.post("/api/v1/signup", json={'phone_number': generated_phone_number})
    data: dict = response.json()

    assert response.status_code == 200
    assert data.get("sms_expires_at")


def test_confirm_sms(client, generated_phone_number):


    code = BaseSmsService.get_code(generated_phone_number)  # "Received the code"
    prepared_data = {"phone_number": generated_phone_number, "sms_code": code}
    data_response = client.post("/api/v1/confirm-sms", json=prepared_data).json()

    new_password = data_response.get("new_password")
    assert data_response.get("access_token")
    assert new_password

    client.new_password = new_password


def test_incorrect_login(client, generated_phone_number):
    password = "incorrect"
    response = client.post(
        "/api/v1/login", json={"phone_number": generated_phone_number, "password": password}
    )
    assert response.status_code == 401


def test_login(client, generated_phone_number):
    password = getattr(client, "new_password")
    response = client.post(
        "/api/v1/login", json={"phone_number": generated_phone_number, "password": password}
    )
    response_data = response.json()

    assert response.status_code == 200
    assert response_data.get("access_token")
