__all__ = ('BaseSmsService', 'SmsServiceLogger')

import logging
from abc import abstractmethod, ABC
from datetime import datetime, timedelta

from apscheduler.job import Job

from src.authorization import config
from src.authorization.mobilephonenumber import MobilePhoneNumber
from src.authorization.smsservice.smscode import SmsCode, generate_code
from src.datehelpers import get_aware_datetime_now
from src.i18n import translate
from src.scheduling import scheduler


SmsServiceLogger: logging.Logger = logging.getLogger("SmsService")


class BaseSmsService(ABC):

    _storage: dict[MobilePhoneNumber, SmsCode] = {}

    @classmethod
    def _clear_task(cls, task_key: MobilePhoneNumber) -> None:

        job: Job | None = scheduler.get_job(task_key, jobstore="sms_service")
        if job:
            scheduler.remove_job(task_key, jobstore="sms_service")
        cls._storage.pop(task_key, "")

    @classmethod
    def _store_temporary_code(cls, code: SmsCode, phone_number: MobilePhoneNumber) -> datetime:

        cls._clear_task(phone_number)
        cls._storage[phone_number] = code

        expires_at = get_aware_datetime_now() + timedelta(seconds=config.SMS_CONFIRMATION_LIFESPAN_SEC)
        scheduler.add_job(
            cls.__remove_code,
            args=(phone_number,),
            trigger="date",
            run_date=expires_at,
            id=phone_number,
            jobstore="sms_service",
        )

        return expires_at

    @classmethod
    def verify_code(cls, phone_number: MobilePhoneNumber, code: SmsCode) -> bool:

        verifying_code: SmsCode = cls._storage.get(phone_number, "")
        if verifying_code != code:
            return False

        cls._clear_task(phone_number)
        return True

    @classmethod
    def __remove_code(cls, phone_number: MobilePhoneNumber) -> None:
        cls._storage.pop(phone_number, "")

        SmsServiceLogger.debug(f"Phone number {phone_number} data cleared")

    @classmethod
    @abstractmethod
    def _send_sms(cls, phone_number: MobilePhoneNumber, message: str) -> dict:
        ...

    @classmethod
    def get_code(cls, phone_number: MobilePhoneNumber) -> SmsCode | None:
        return cls._storage.get(phone_number)

    @classmethod
    def send_sms_verification(cls, phone_number: MobilePhoneNumber, language: str) -> datetime:
        """
        :param phone_number: phone number to send
        :param language: SMS message confirmation language
        :return: SMS-code expiration datetime
        """

        sms_code = generate_code(config.SMS_GENERATED_CODE_LENGTH)
        message = translate(
            "IamNotAlone service. Your authorization code: {sms_code}", language=language
        ).format(sms_code=sms_code)

        if not config.SMS_SERVICE_DISABLED:
            cls._send_sms(phone_number, message)

        expires_at: datetime = cls._store_temporary_code(sms_code, phone_number)

        SmsServiceLogger.info(
            "SMS(code=%s, lang=%s, expires_at=%s, test=%s) sent to %s",
            sms_code, language, expires_at, config.SMS_SERVICE_DISABLED, phone_number
        )
        return expires_at

