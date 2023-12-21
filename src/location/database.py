__all__ = ("geonames_db",)

import typing

from pycities import CityDatabase, RowFactoryModelConfig, config, dict_factory
from pycities.model import TCityModel

from location.cityrow import CityRow


class CityDb(CityDatabase, typing.Generic[TCityModel]):

    def get_city_by_row_id(self, row_id: int, lang: str = "") -> None | CityRow:
        select_query = self._prepare_select_template(
            self.fetch_fields,
            (f"{config.CITY_SELECT_TEMPLATE}"
             f"LIMIT 1 OFFSET ?"),
            lang=lang
        )
        result = self.cursor.execute(select_query, (row_id,))
        return result.fetchone()


RowFactoryModelConfig.set(CityRow, lambda cursor, row: CityRow(**dict_factory(cursor, row)))
geonames_db = CityDb[CityRow](
    fetch_fields=("id", "name", "administrative_name", "country_name", "longitude", "latitude")
)

