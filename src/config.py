import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


BASE_DIR: Path = Path(__file__).parent.parent
ROOT_DIR: str = os.path.dirname(os.path.abspath(__file__))
DATA_PATH: str = os.path.join(BASE_DIR, "data")

SERVER_URL: str = os.getenv("SERVER_URL", "http://127.0.0.1:8000")
IMAGE_HOSTS: list[str] = os.getenv("IMAGE_HOSTS", "127.0.0.1").split(", ")

STATIC_PATH: str = os.path.join(BASE_DIR, "static")

if not os.path.exists(STATIC_PATH):
    os.makedirs(STATIC_PATH)

DB_USER: str = os.getenv("DB_USER", "admin")
DB_PASSWORD: str = os.getenv("DB_PASSWORD", "secretmongo")
DB_NAME: str = os.getenv("DB_NAME", "iamnotalone")
DB_HOST: str = os.getenv("DB_HOST", "localhost")

DB_GEONAMES_DATA_SOURCE: str = os.path.join(DATA_PATH, "geo", "data.db")

ACCESS_TOKEN_EXPIRE_DAYS: int = 14
AUTH_ALGORYTHM: str = os.getenv("AUTH_ALGORYTHM", "HS256")
AUTH_SECRET_KEY: str = os.getenv(
    "AUTH_SECRET_KEY", "3dc281d0e64ca7cb956e88ce394a7b559710aa623675dd0148530f49cf777423"
)
AUTH_HEADER_TYPE: str = "Bearer"

i18n_DOMAIN: str = "base"
i18n_DEFAULT_LANGUAGE: str = "en"
i18n_LOCALES_PATH: str = os.path.join(DATA_PATH, "locales")
i18n_SUPPORTED_LANGUAGES: tuple[str, ...] = tuple(
    lang for lang in os.listdir(i18n_LOCALES_PATH) if os.path.isdir(os.path.join(i18n_LOCALES_PATH, lang))
)




