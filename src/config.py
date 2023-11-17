import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


BASE_DIR: Path = Path(__file__).parent.parent
DATA_PATH: Path = BASE_DIR / "data"
STATIC_PATH: Path = BASE_DIR / "static"
if not STATIC_PATH.exists():
    STATIC_PATH.mkdir()

SERVER_URL: str = os.getenv("SERVER_URL", "http://127.0.0.1:8000")

DB_USER: str = os.getenv("DB_USER", "admin")
DB_PASSWORD: str = os.getenv("DB_PASSWORD", "secretmongo")
DB_NAME: str = os.getenv("DB_NAME", "iamnotalone")
DB_HOST: str = os.getenv("DB_HOST", "localhost")


ACCESS_TOKEN_EXPIRE_DAYS: int = 14
AUTH_ALGORYTHM: str = os.getenv("AUTH_ALGORYTHM", "HS256")
AUTH_SECRET_KEY: str = os.getenv(
    "AUTH_SECRET_KEY", "3dc281d0e64ca7cb956e88ce394a7b559710aa623675dd0148530f49cf777423"
)

i18n_DOMAIN: str = "base"
i18n_DEFAULT_LANGUAGE: str = "en"
i18n_LOCALES_PATH: Path = DATA_PATH / "locales"

i18n_SUPPORTED_LANGUAGES: frozenset[str, ...] = frozenset(
    lang for lang in os.listdir(i18n_LOCALES_PATH) if (i18n_LOCALES_PATH / lang).is_dir()
)
