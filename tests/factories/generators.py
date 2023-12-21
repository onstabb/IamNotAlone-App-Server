from random import Random


from authorization.phonenumber import validate_mobile_phone_number
from security import generate_password, hash_password
from location.cityrow import CityRow

from location.database import geonames_db



def _get_random(random_obj: Random | None = None) -> Random:
    if not random_obj:
        from factory.random import randgen
        random_obj = randgen
    return random_obj


def generate_random_mobile_number(random: Random | None = None) -> str:
    random = _get_random(random)
    while True:
        number = "+380" + str(random.randint(50, 99)) + str(random.randint(1000000, 9999999))
        try:
            return validate_mobile_phone_number(number)
        except ValueError:
            pass


def generate_hashed_password() -> str:
    return hash_password(generate_password())


def get_random_city(random: Random | None = None) -> CityRow:
    random =  _get_random(random)
    city = geonames_db.get_city_by_row_id(random.randint(0, 15760))
    return city
