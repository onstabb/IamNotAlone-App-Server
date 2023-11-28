from fastapi import Request

from starlette_admin import PhoneField, row_action
from starlette_admin.contrib.mongoengine import ModelView
from starlette_admin.exceptions import ActionFailed

from reports.models import Report
from users.enums import UserRole
from users.models import User


class UserView(ModelView):
    ACTION_BAN_UNBAN = "ban_unban"
    row_actions = ["edit", "view", "delete", ACTION_BAN_UNBAN]

    fields = [
        "id",
        PhoneField("phone_number"),
        "role",
        "is_active",
        "banned",
        "last_online",
        "photo_urls",
        "profile",
        "events",
    ]
    exclude_fields_from_edit = ["phone_number", ]
    exclude_fields_from_list = ["profile.location", "events"]

    def can_create(self, request: Request) -> bool:
        return UserRole.ADMIN == request.state.user.role

    def can_edit(self, request: Request) -> bool:
        return UserRole.ADMIN == request.state.user.role

    async def is_row_action_allowed(self, request: Request, name: str) -> bool:
        if name == self.ACTION_BAN_UNBAN:
            return request.state.user.role in UserRole.managers()
        return await super().is_row_action_allowed(request, name)

    @row_action(
        name=ACTION_BAN_UNBAN,
        text="Ban/Unban user",
        confirmation="Are you sure you want to ban/unban this user?",
        submit_btn_text="Yes, proceed",
        submit_btn_class="btn-success",
        action_btn_class="btn-danger",
        icon_class="fa-solid fa-ban",
    )
    async def ban_action(self, request: Request, pk: str) -> str:
        user = User.get_one(id=pk)
        if not user:
            raise ActionFailed("Incorrect user")

        if user.role in UserRole.managers():
            raise ActionFailed("You cannot perform this action with this user")

        user.banned = not user.banned
        user.save()
        return f"User {user.id} banned status is {user.banned}"


class EventView(ModelView):
    fields = [
        "id",
        "title",
        "start_at",
        "city_id",
        "description",
        "location",
        "image_urls",
        "subscribers"
    ]
    exclude_fields_from_list = ["location", "image_urls", "description", "subscribers"]


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


class ReportView(ModelView):
    ACTION_CLOSE = "close"
    row_actions = ["view", "delete", "edit", ACTION_CLOSE]

    fields = [
        "initiator",
        "respondent",
        "reason",
        "additional_info",
        "closed",
    ]

    @row_action(
        name=ACTION_CLOSE,
        text="Close report",
        action_btn_class="btn-success",
        icon_class="fas fa-check-circle",
    )
    async def close_report(self, request: Request, pk: str) -> str:
        report = Report.get_one(id=pk)
        if not report:
            raise ActionFailed("Incorrect report")

        if report.closed:
            raise ActionFailed("This report is already closed")

        report.closed = True
        report.save()
        return f"Report {report.id} successfully closed"

    def can_create(self, request: Request) -> bool:
        return UserRole.ADMIN == request.state.user.role

    def can_edit(self, request: Request) -> bool:
        return UserRole.ADMIN == request.state.user.role

    def can_delete(self, request: Request) -> bool:
        return UserRole.ADMIN == request.state.user.role