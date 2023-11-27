from fastapi import Request

from starlette_admin import PhoneField
from starlette_admin.contrib.mongoengine import ModelView

from users.enums import UserRole


class UserView(ModelView):
    fields = [
        "id",
        PhoneField("phone_number"),
        "is_active",
        "banned",
        "photo_urls",
        "profile",
        "last_online",
    ]
    exclude_fields_from_edit = ["phone_number", ]
    exclude_fields_from_list = ["profile.location", ]

    def can_create(self, request: Request) -> bool:
        return UserRole.ADMIN == request.state.user.role



class EventView(ModelView):
    fields = [
        "id",
        "title",
        "start_at",
        "city_id",
        "description",
        "location",
        "image_urls",
    ]
    exclude_fields_from_list = ["location", "image_urls", "description"]




class ContactView(ModelView):
    fields = [
        "initiator",
        "respondent",
        "initiator_state",
        "respondent_state",
        "status",
        "messages"
    ]

    exclude_fields_from_list = ["messages"]
    exclude_fields_from_edit = ["messages"]

    def can_create(self, request: Request) -> bool:
        return UserRole.ADMIN == request.state.user.role

    def can_edit(self, request: Request) -> bool:
        return UserRole.ADMIN == request.state.user.role

