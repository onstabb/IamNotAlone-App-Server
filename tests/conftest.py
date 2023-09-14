
import pytest
from fastapi.testclient import TestClient
from mongomock import MongoClient


from src import config
from src.authorization import config as auth_config
from src.database import init_db, close_db
from src.geodata.database import geonames_db
from src.main import app
from src.scheduling import scheduler

from tests.factories.generators import generate_random_mobile_number


def _db_prepare():
    from factory import random

    random.reseed_random("252525")


def _db_clear(db) -> None:
    db.drop_database(config.DB_NAME)

@pytest.fixture(scope="session")
def factory_random():
    from factory import random
    yield random


@pytest.fixture(scope="session")
def db_mock_config():
    db = init_db(host=config.DB_HOST, db=config.DB_NAME, mongo_client_class=MongoClient)
    _db_prepare()
    yield db
    close_db()


@pytest.fixture(scope="session")
def db_config():
    db = init_db(host=config.DB_HOST, db=config.DB_NAME)
    _db_clear(db)
    _db_prepare()
    yield db

    close_db()

@pytest.fixture(scope="session")
def client(db_config):
    auth_config.SMS_SERVICE_DISABLED = True

    scheduler.start()
    geonames_db.connect(config.DB_GEONAMES_DATA_SOURCE)
    client = TestClient(app=app)

    yield client

    scheduler.shutdown()
    geonames_db.close()


@pytest.fixture()
def user_factory(db_config):
    from tests.factories.factories import UserFactory
    yield UserFactory



