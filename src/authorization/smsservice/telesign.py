import logging

from fastapi import HTTPException, status
from telesign.messaging import MessagingClient
from telesign.rest import RestClient

from src.authorization import config
from src.authorization.smsservice.baseservice import BaseSmsService

log: logging.Logger = logging.getLogger(__name__)


class TelesignService(BaseSmsService):

    _client: MessagingClient = MessagingClient(config.SMS_CUSTOMER_ID, config.SMS_API_KEY)

    @classmethod
    def _send_sms(cls, phone_number: str, message: str) -> dict:
        response: RestClient.Response = cls._client.message(
            phone_number=phone_number, message=message, message_type="OTP"
        )
        response_message: str = f'http code: {response.status_code}, {response.json}'

        if response.status_code == 200:
            return response.json

        log.error(response_message)

        match response.status_code:
            case 400: raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE)
            case 503: raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
            case _: raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
