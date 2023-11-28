import os

import pytest
from factory import random
from starlette.testclient import TestClient

import config
from authorization import config as auth_config
from database import init_db, close_db
from factories import factories
from location.database import geonames_db
from main import app
from photos.service import set_bucket
from photos.bucket.local import LocalBucket
from scheduling import scheduler as scheduler_
from users.models import User


ROOT_DIR = config.BASE_DIR / "tests"
DATA_DIR = ROOT_DIR / "data"

TEST_DB_URI = os.getenv("TEST_DB_URI")
TEST_DB_NAME = os.getenv("TEST_DB_NAME", "iamnotalone")


class AppTestClient(TestClient):

    @property
    def bearer_token(self):
        return self.headers.get("Authorization")

    @bearer_token.setter
    def bearer_token(self, new_token: str) -> None:
        self.headers = {"Authorization": f"Bearer {new_token}"}


@pytest.fixture(scope="session")
def seed():
    return 131313


@pytest.fixture(scope="session")
def factory_random(seed):
    random.reseed_random(seed)
    return random


@pytest.fixture(scope="session")
def scheduler():
    scheduler_.start()
    yield scheduler_
    scheduler_.shutdown()


@pytest.fixture(scope="session")
def city_db():
    geonames_db.connect()
    yield geonames_db
    geonames_db.close()


@pytest.fixture(scope="session")
def db_config(factory_random):
    db = init_db(host=TEST_DB_URI, db=TEST_DB_NAME)
    db.drop_database(config.DB_NAME)
    factory_random.reseed_random(131313)
    yield db
    close_db()


@pytest.fixture(scope="function")
def client(db_config, scheduler, city_db):
    auth_config.SMS_SERVICE_DISABLED = True
    set_bucket(LocalBucket())
    client = AppTestClient(app=app)
    yield client
    client.close()


@pytest.fixture(scope="session")
def user_factory(db_config, city_db):
    return factories.UserFactory


@pytest.fixture(scope="session")
def contact_factory(db_config, city_db):
    return factories.ContactFactory


@pytest.fixture(scope="session")
def userprofile_factory(db_config, city_db):
    return factories.ProfileFactory


@pytest.fixture(scope="session")
def event_factory(db_config, city_db):
    return factories.EventFactory


@pytest.fixture(scope="session")
def report_factory(db_config, city_db):
    return factories.ReportFactory


@pytest.fixture(scope="function")
def user(user_factory) -> User:
    user: User = user_factory.create()
    return user


@pytest.fixture(scope="function")
def authorized_user(client, user) -> User:
    client.bearer_token = user.token[0]
    return user
