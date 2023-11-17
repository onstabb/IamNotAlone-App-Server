import os

SMS_CONFIRMATION_LIFESPAN_SEC: int = 120

SMS_SERVICE_DISABLED = bool(os.getenv("SMS_SERVICE_DISABLED", True))
SMS_CUSTOMER_ID: str = os.getenv("SMS_CUSTOMER_ID")
SMS_API_KEY: str = os.getenv("SMS_API_KEY")
SMS_GENERATED_CODE_LENGTH: int = 5
