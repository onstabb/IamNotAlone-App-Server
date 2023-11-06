import os

import pytest
from factory import random
from fastapi.testclient import TestClient


import config
import security
from authorization import config as auth_config
from authorization.models import User
from database import init_db, close_db
from files import config as file_config
from files import service as file_service
from geodata.database import geonames_db
from main import app
from scheduling import scheduler as scheduler_


ROOT_DIR = os.path.join(config.BASE_DIR, "tests")
DATA_DIR = os.path.join(ROOT_DIR, "data")

def _db_clear(db) -> None:
    db.drop_database(config.DB_NAME)


def get_auth_headers(user: User) -> dict:
    headers = {
        "Authorization": f"Bearer {security.create_access_token(user.id, security.get_token_expiration_from_now())}"
    }
    return headers


@pytest.fixture(scope="session")
def seed():
    return 131313


@pytest.fixture(scope="session")
def factory_random(seed):
    random.reseed_random(seed)
    return random


@pytest.fixture(scope="session")
def temp_file_storage(tmp_path_factory):
    file_config.IMAGE_FILES_LOCAL_PATH = tmp_path_factory.mktemp("data")
    return file_config.IMAGE_FILES_LOCAL_PATH


@pytest.fixture(scope="session")
def scheduler():
    scheduler_.start()
    yield scheduler_
    scheduler_.shutdown()


@pytest.fixture(scope="session")
def city_db():
    geonames_db.connect(config.DB_GEONAMES_DATA_SOURCE)
    yield geonames_db
    geonames_db.close()


@pytest.fixture(scope="session")
def db_config(factory_random):
    db = init_db(host=config.DB_HOST, db=config.DB_NAME)
    _db_clear(db)
    factory_random.reseed_random(131313)
    yield db
    close_db()


@pytest.fixture(scope="session")
def client(db_config, scheduler, city_db, temp_file_storage):
    auth_config.SMS_SERVICE_DISABLED = True
    client = TestClient(app=app)
    yield client
    client.close()


@pytest.fixture(scope="session")
def user_factory(db_config, city_db):
    from factories.factories import UserFactory
    return UserFactory


@pytest.fixture(scope="session")
def _prepare_test_user_auth(user_factory) -> tuple[dict, User]:
    user: User = user_factory.create(profile=None)
    return get_auth_headers(user), user


@pytest.fixture(scope="session")
def auth_headers_user_without_profile(_prepare_test_user_auth):
    headers, user = _prepare_test_user_auth
    return headers


@pytest.fixture(scope="session")
def authorization(_prepare_test_user_auth):
    from factories.factories import ProfileFactory
    headers, user = _prepare_test_user_auth
    profile = ProfileFactory.create()
    user.profile = profile
    user.save()
    return headers
