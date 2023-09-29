import os
import shutil

import pytest
from fastapi import UploadFile
from fastapi.testclient import TestClient
from mongomock import MongoClient


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
    yield 131313


@pytest.fixture(scope="session")
def factory_random(seed):
    from factory import random
    random.reseed_random(seed)
    yield random


@pytest.fixture(scope="session")
def image_file_storage_conf():
    storage_dir = os.path.join(DATA_DIR, "Image Storage")
    if not os.path.exists(storage_dir):
        os.mkdir(storage_dir)
    file_config.IMAGE_FILES_LOCAL_PATH = storage_dir
    yield
    shutil.rmtree(storage_dir)


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
def db_mock_config():
    db = init_db(host=config.DB_HOST, db=config.DB_NAME, mongo_client_class=MongoClient, )
    yield db
    close_db()


@pytest.fixture(scope="session")
def db_config(factory_random):
    db = init_db(host=config.DB_HOST, db=config.DB_NAME)
    _db_clear(db)
    factory_random.reseed_random(131313)
    yield db
    close_db()


@pytest.fixture()
def client(db_config, scheduler, city_db, image_file_storage_conf):
    auth_config.SMS_SERVICE_DISABLED = True
    client = TestClient(app=app)
    yield client


@pytest.fixture(scope="session")
def user_factory(db_config, city_db):
    from factories.factories import UserFactory
    yield UserFactory


@pytest.fixture(scope="session")
def _prepare_test_user_auth(user_factory):
    user = user_factory.create(profile=None)

    yield get_auth_headers(user), user


@pytest.fixture(scope="session")
def authorization_user_only(_prepare_test_user_auth):
    headers, user = _prepare_test_user_auth
    yield headers


@pytest.fixture(scope="session")
def user_image_url(_prepare_test_user_auth):
    headers, user = _prepare_test_user_auth
    filename = "Test2.png"
    upload_file = UploadFile(open(os.path.join(DATA_DIR, "images", filename), "rb"), filename=filename,)
    token = file_service.save_image_and_create_token(upload_file, user.id)
    yield f"{file_config.SERVER_STATIC_URL}/{token}"


@pytest.fixture(scope="session")
def authorization(_prepare_test_user):
    from factories.factories import ProfileFactory
    headers, user = _prepare_test_user
    profile = ProfileFactory.create()
    user.profile = profile
    user.save()
    yield headers
