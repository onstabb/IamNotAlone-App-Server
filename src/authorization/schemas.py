from datetime import datetime

from pydantic import BaseModel, SecretStr

from authorization.phonenumber import MobilePhoneNumber
from authorization.smsservice.smscode import SmsCode


class SignUpDataIn(BaseModel):
    phone_number: MobilePhoneNumber


class UserCredentialsIn(SignUpDataIn):
    password: SecretStr


class SmsConfirmationDataIn(SignUpDataIn):
    sms_code: SmsCode


class SmsConfirmationDataOut(BaseModel):
    sms_expires_at: datetime


class TokenDataOut(BaseModel):
    access_token: str
    expires_at: datetime
    new_password: str | None = None
