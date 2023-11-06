__all__ = ("geonames_db",)

import logging
from sqlite3 import connect, Connection, Cursor

import config
from geodata import helpers
from geodata.geopoint import GeoPoint
from geodata.cityrow import CityRow


log = logging.getLogger(__name__)

def _convert_row(_cursor: Cursor, row: tuple) -> CityRow | int:

    if len(row) == 1:
        return row[0]

    data = {field: row[index] for index, field in enumerate(CityRow.model_fields, )}
    data['coordinates'] = data['coordinates'].split(";")
    return CityRow(**data)


class GeoNamesSqlite:

    _SELECT_NEAREST_CITY = """
SELECT DISTINCT
    city.geonameid AS geonameid,
    city.name AS city_name,
    city.latitude || ';' || city.longitude AS coordinates,
    administrative_unit.name AS administrative_unit_name,
    country.name AS country_name,
    country.iso AS country_code
FROM
    city
JOIN
    administrative_unit ON city.administrative_unit_id = administrative_unit.id
JOIN
    country ON administrative_unit.country_id = country.id
ORDER BY 
    DISTANCE(city.longitude, city.latitude, ?, ?)  
LIMIT ?
    
    """

    _SELECT_CITY_BY_ROW_ID = """
SELECT DISTINCT
    city.geonameid AS geonameid,
    city.name AS city_name,
    city.longitude  || ';' || city.latitude  AS coordinates,
    administrative_unit.name AS administrative_unit_name,
    country.name AS country_name,
    country.iso AS country_code
FROM
    city
JOIN
    administrative_unit ON city.administrative_unit_id = administrative_unit.id
JOIN
    country ON administrative_unit.country_id = country.id
ORDER BY 
    city.geonameid
LIMIT 1
OFFSET ?  
    """

    _SELECT_GEONAMEID_QUERY = """
SELECT DISTINCT
    city.geonameid AS geonameid,
    city.name AS city_name,
    city.latitude || ';' || city.longitude AS coordinates,
    administrative_unit.name AS administrative_unit_name,
    country.name AS country_name,
    country.iso AS country_code
FROM
    city
JOIN
    administrative_unit ON city.administrative_unit_id = administrative_unit.id
JOIN
    country ON administrative_unit.country_id = country.id
WHERE
    city.geonameid = ?
    """

    _SELECT_SEARCH_QUERY = """

SELECT DISTINCT
    city.geonameid AS geonameid,
    city.name AS city_name,
    administrative_unit.name AS administrative_unit_name,
    country.name AS country_name,
    country.iso AS country_code
FROM
    city
JOIN
    administrative_unit ON city.administrative_unit_id = administrative_unit.id
JOIN
    country ON administrative_unit.country_id = country.id
JOIN
    alternate_name ON city.geonameid = alternate_name.geonameid
WHERE
    alternate_name.name LIKE ? || '%' COLLATE NOCASE
GROUP BY
    city.geonameid
    """

    def __init__(self) -> None:
        self.__conn: Connection | None = None
        self.__cursor: Cursor | None = None

    def connect(self, data_source: str = config.DB_GEONAMES_DATA_SOURCE) -> None:

        self.__conn = connect(data_source, check_same_thread=False)
        self.__conn.create_function("DISTANCE", 4, helpers.calculate_distance_, deterministic=True)
        self.__conn.row_factory = _convert_row
        self.__cursor = self.__conn.cursor()
        log.info('Connected source "%s""', data_source)

    def search_cities(self, query: str) -> list[CityRow]:
        query = query.capitalize()
        result: Cursor = self.__cursor.execute(self._SELECT_SEARCH_QUERY, (query,))
        return result.fetchall()

    def get_city(self, geonameid: int) -> CityRow | None:
        result: Cursor = self.__cursor.execute(self._SELECT_GEONAMEID_QUERY, (geonameid,))
        return result.fetchone()

    def get_nearest_cities(self, coordinates: GeoPoint, limit: int = 3) -> list[CityRow]:
        result: Cursor = self.__cursor.execute(
            self._SELECT_NEAREST_CITY,(coordinates[0], coordinates[1], limit)
        )
        return result.fetchall()

    def get_nearest_city(self, coordinates: GeoPoint) -> CityRow:
        return self.get_nearest_cities(coordinates, limit=1)[0]

    def get_city_by_row_id(self, index: int) -> CityRow:
        result: Cursor = self.__cursor.execute(self._SELECT_CITY_BY_ROW_ID, (index,))
        return result.fetchone()

    def get_city_count(self) -> int:
        return self.__cursor.execute("SELECT COUNT(geonameid) FROM city").fetchone()

    def close(self) -> None:
        self.__cursor.close()
        self.__conn.close()
        log.info("Disconnected")


geonames_db = GeoNamesSqlite()

