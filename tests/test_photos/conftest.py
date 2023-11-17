import pytest

from conftest import DATA_DIR


@pytest.fixture(scope="function")
def image_file():
    return open(DATA_DIR / 'images' / "Test1.jpg", "rb+")
