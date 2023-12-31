import os

SMS_CONFIRMATION_LIFESPAN_SEC: int = 120

AUTH_GENERATED_PASSWORD_LENGTH: int = 8


SMS_SERVICE_DISABLED: bool = bool(os.getenv("SMS_SERVICE_DISABLED", True))
SMS_CUSTOMER_ID: str = os.getenv("SMS_CUSTOMER_ID", "A54704AE-AEC7-4942-ADC4-D8C46B54AD7E")
SMS_API_KEY: str = os.getenv(
    "SMS_API_KEY", "J3rfe+DZA9NZxA05JMrgufLUJVqpXh1dNytAqmgq4nOsI2POWX26Pse1wvYhUbgqh1NbF+mlPt46CkhUZMhe5A=="
)
SMS_GENERATED_CODE_LENGTH: int = 5
