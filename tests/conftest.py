
import pytest
from fastapi.testclient import TestClient
from mongomock import MongoClient


from src import config
from src.authorization import config as auth_config
from src.database import init_db, close_db
from src.geodata.database import geonames_db
from src.main import app
from src.scheduling import scheduler as scheduler_



def _db_clear(db) -> None:
    db.drop_database(config.DB_NAME)

@pytest.fixture(scope="session")
def seed():
    yield 131313

@pytest.fixture(scope="session")
def factory_random(seed):
    from factory import random
    random.reseed_random(seed)
    yield random

@pytest.fixture(scope="session")
def scheduler():
    scheduler_.start()
    yield scheduler_
    scheduler_.shutdown()


@pytest.fixture(scope="session")
def db_mock_config():
    db = init_db(host=config.DB_HOST, db=config.DB_NAME, mongo_client_class=MongoClient)
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
def client(db_config, scheduler):
    auth_config.SMS_SERVICE_DISABLED = True

    geonames_db.connect(config.DB_GEONAMES_DATA_SOURCE)
    client = TestClient(app=app)

    yield client

    geonames_db.close()


@pytest.fixture()
def user_factory(db_config):
    from tests.factories.factories import UserFactory
    yield UserFactory





