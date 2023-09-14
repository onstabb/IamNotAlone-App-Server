from random import Random


from src.authorization.mobilephonenumber import validate_mobile_phone_number
from src.authorization.password import build_password, get_password_hash
from src.geodata import service as geodata_service
from src.geodata.database import geonames_db
from src.geodata.models import City


def _get_random(random_obj: Random | None = None) -> Random:
    if not random_obj:
        from factory.random import randgen
        random_obj = randgen
    return random_obj


# def generate_adult_date(random: Random | None = None) -> date:
#     random = _get_random(random)
#     today = date.today()
#
#     return date(
#         year=today.year - random.randint(profile_config.MIN_AGE + 1, profile_config.MAX_AGE - 1),
#         month=random.randint(1, 12),
#         day=random.randint(1, 28)
#     )


def generate_random_mobile_number(random: Random | None = None) -> str:
    random = _get_random(random)

    while True:
        number = "+380" + str(random.randint(50, 99)) + str(random.randint(1000000, 9999999))

        try:
            return validate_mobile_phone_number(number)
        except ValueError:
            pass


def generate_hashed_password() -> str:
    return get_password_hash(build_password())


def create_random_city(random: Random | None = None) -> City:
    random =  _get_random(random)
    city = geodata_service.create_city_if_not_exists(
        geonames_db.get_city_by_row_id(
            random.randint(0, geonames_db.get_city_count())
        )
    )
    return city

