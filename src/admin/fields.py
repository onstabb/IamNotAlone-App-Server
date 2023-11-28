from dataclasses import dataclass
from typing import Any, Sequence

from starlette.datastructures import FormData
from starlette.requests import Request
from starlette_admin import fields as admin_fields, RequestAction

from location.database import geonames_db


@dataclass
class PointField(admin_fields.FloatField):
    form_template: str = "forms/geopoint.html"
    display_template: str = "displays/geopoint.html"

    async def parse_form_data(
        self, request: Request, form_data: FormData, action: RequestAction
    ) -> Sequence[float] | None:
        try:
            longitude = float(form_data.get(self.id + ".longitude"))
            latitude = float(form_data.get(self.id + ".latitude"))
        except ValueError:
            return None

        return longitude, latitude

    async def serialize_value(
        self, request: Request, value: dict, action: RequestAction
    ) -> Any:
        return dict(value)


class CityField(admin_fields.IntegerField):

    async def serialize_value(
        self, request: Request, value: Any, action: RequestAction
    ) -> Any:

        if action in (RequestAction.EDIT, RequestAction.CREATE):
            return int(value)

        return str(geonames_db.get_city(value))