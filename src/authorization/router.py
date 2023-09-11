from fastapi import APIRouter, Header, HTTPException, status, Depends


from src.authorization import service, dependencies
from src.authorization.models import User
from src.authorization.password import build_password, verify_password
from src.authorization.schemas import (
    SignUpDataIn, TokenDataOut, SmsConfirmationDataIn, SmsConfirmationDataOut, UserOut, UserIn
)
from src.authorization.smsservice.telesign import TelesignService
from src.security import create_access_token, get_token_expiration_from_now

router: APIRouter = APIRouter(tags=['auth'])


@router.post("/signup", response_model=SmsConfirmationDataOut)
def sign_up(data: SignUpDataIn, accept_language: str = Header(default="en", max_length=2, example="uk")):
    expires_at = TelesignService.send_sms_verification(data.phone_number, accept_language)
    return SmsConfirmationDataOut(sms_expires_at=expires_at)


@router.post("/confirm-sms", response_model=TokenDataOut)
def confirm_sms(data: SmsConfirmationDataIn):
    if not TelesignService.verify_code(data.phone_number, data.sms_code):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'SMS-code is invalid')

    generated_password: str = build_password()

    user: User | None = service.get_user(data.phone_number)

    user = service.update_user_password(user, generated_password) \
        if user else service.create_user(data.phone_number, generated_password)

    access_token_expires_at = get_token_expiration_from_now()

    return TokenDataOut(
        access_token=create_access_token(subject=user.id, expires_at=access_token_expires_at),
        new_password=generated_password,
        expires_at=access_token_expires_at
    )


@router.post("/login", response_model=TokenDataOut, response_model_exclude_none=True)
def login(user_in: UserIn):

    user: User | None = service.get_user(user_in.phone_number)

    if not user or not verify_password(user_in.password.get_secret_value(), user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid phone number or password",
        )

    access_token_expires_at = get_token_expiration_from_now()
    return TokenDataOut(
        access_token=create_access_token(subject=user.id, expires_at=access_token_expires_at),
        new_password=None,
        expires_at=access_token_expires_at,
    )


@router.get("/user/me", response_model=UserOut)
def get_user(user: User = Depends(dependencies.get_unbanned_user)):
    return user

