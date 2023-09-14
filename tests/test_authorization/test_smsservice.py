import pytest

from authorization.smsservice.baseservice import BaseSmsService


@pytest.fixture
def phone_number(scheduler):
    number = "+48888888888"
    BaseSmsService.send_sms_verification(number, language="uk")
    yield number


def test_send_sms_expiration_task_created(phone_number, scheduler):
    assert scheduler.get_job(phone_number)


def test_verify_and_clear_correct_code(phone_number):
    code = BaseSmsService.get_code(phone_number)
    assert BaseSmsService.verify_code_and_clear(phone_number, code)
    assert not BaseSmsService.verify_code_and_clear(phone_number, code)


def test_verify_and_clear_incorrect_code(phone_number):

    code = BaseSmsService.get_code(phone_number)
    assert not BaseSmsService.verify_code_and_clear(phone_number, "wrong")
    assert BaseSmsService.verify_code_and_clear(phone_number, code)

