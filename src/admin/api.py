from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin.contrib.mongoengine import Admin

from admin import config, views
from admin.auth import AdminCredentialsProvider
from admin.converter import MongoengineModelConverter

from config import DATA_PATH
from contacts.models import Contact
from events.models import Event
from reports.models import Report
from users.models import User



admin = Admin(
    templates_dir=str(DATA_PATH / "templates" / "admin"),
    auth_provider=AdminCredentialsProvider(),
    middlewares=[Middleware(SessionMiddleware, secret_key=config.SESSION_SECRET_KEY)]
)
_converter = MongoengineModelConverter()

admin.add_view(views.UserView(User, converter=_converter, icon="fa-solid fa-users"))
admin.add_view(views.ContactView(Contact, converter=_converter, icon="fa-solid fa-people-arrows"))
admin.add_view(views.EventView(Event, converter=_converter, icon="fa-solid fa-calendar-day"))
admin.add_view(views.ReportView(Report, converter=_converter, icon="fa-solid fa-flag"))