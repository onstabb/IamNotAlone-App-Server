from fastapi import APIRouter, Header, HTTPException, status

import config as global_config

from authorization import service
from authorization.schemas import (
    SignUpDataIn, TokenDataOut, SmsConfirmationDataIn, SmsConfirmationDataOut, UserCredentialsIn
)
from authorization.smsservice.telesign import TelesignService
from users.models import User
from security import generate_password, hash_password


router: APIRouter = APIRouter(tags=['Authorization'])


@router.post("/signup", response_model=SmsConfirmationDataOut)
def sign_up(
        data: SignUpDataIn,
        accept_language: str = Header(
            default=global_config.i18n_DEFAULT_LANGUAGE,
            max_length=2,
            examples=list(global_config.i18n_SUPPORTED_LANGUAGES)
        )
):
    expires_at = TelesignService.send_sms_verification(data.phone_number, accept_language)
    return SmsConfirmationDataOut(sms_expires_at=expires_at)


@router.post("/confirm-sms", response_model=TokenDataOut)
def confirm_sms(data: SmsConfirmationDataIn):
    if not TelesignService.verify_code_and_clear(data.phone_number, data.sms_code):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'SMS-code is invalid')

    generated_password: str = generate_password()
    hashed_password = hash_password(generated_password)

    user: User | None = service.get_user_by_phone_number(data.phone_number)
    user = (
        service.update_user_password(user, hashed_password)
        if user else service.create_user(data.phone_number, hashed_password)
    )
    token, expires_at = user.token
    return TokenDataOut(access_token=token, new_password=generated_password, expires_at=expires_at)


@router.post("/login", response_model=TokenDataOut, response_model_exclude_none=True)
def login(user_in: UserCredentialsIn):
    user: User | None = service.get_user_by_phone_number(user_in.phone_number)
    if not user or not user.check_password(user_in.password.get_secret_value()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid phone number or password",
        )

    token, expires_at = user.token
    return TokenDataOut(access_token=token, new_password=None, expires_at=expires_at)
