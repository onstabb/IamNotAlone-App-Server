from datetime import datetime

from pydantic import BaseModel, SecretStr

from src import config
from src.authorization.mobilephonenumber import MobilePhoneNumber
from src.authorization.smsservice.smscode import SmsCode
from src.models import PydanticObjectId


class SignUpDataIn(BaseModel):
    phone_number: MobilePhoneNumber


class UserIn(SignUpDataIn):
    password: SecretStr


class UserOut(BaseModel):
    id: PydanticObjectId
    phone_number: str


class SmsConfirmationDataIn(SignUpDataIn):
    sms_code: SmsCode


class SmsConfirmationDataOut(BaseModel):
    sms_expires_at: datetime


class TokenDataOut(BaseModel):
    access_token: str
    token_type: str = config.AUTH_HEADER_TYPE
    new_password: str | None = None
    expires_at: datetime
