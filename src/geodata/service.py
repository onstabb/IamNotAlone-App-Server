from src.geodata.basetypes import CityRow, GeoPoint
from src.geodata.database import GeoNamesSqlite
from src.geodata.models import City


def create_city_if_not_exists(city_row: CityRow) -> City:
    city_in_db: City | None = City.get_one(geonameid=city_row.geonameid)
    if not city_in_db:
        city_in_db = City(**city_row.model_dump())
        city_in_db.save()
    return city_in_db


def create_nearest_city_if_not_exists(coordinates: GeoPoint) -> City:
    connector = GeoNamesSqlite.get_instance()
    city_row = connector.get_nearest_city(coordinates)

    return create_city_if_not_exists(city_row)