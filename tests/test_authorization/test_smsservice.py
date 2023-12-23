import pytest

from authorization.smsservice.baseservice import BaseSmsService


@pytest.fixture(scope="function")
def phone_number(scheduler):
    number = "+48888888888"
    BaseSmsService.send_sms_verification(number, language="uk")
    return number


def test_send_sms_expiration_task_created(phone_number, scheduler):
    assert scheduler.get_job(phone_number)


def test_verified(phone_number):
    code = BaseSmsService.get_code(phone_number)
    assert BaseSmsService.verified(phone_number, code)


def test_not_verified(phone_number):
    code = BaseSmsService.get_code(phone_number)
    BaseSmsService.clear(phone_number)
    assert not BaseSmsService.verified(phone_number, code)
