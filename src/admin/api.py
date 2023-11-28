from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin.contrib.mongoengine import Admin

from admin import config
from admin.auth import AdminCredentialsProvider
from admin.converter import MongoengineModelConverter
from admin.views import EventView, ContactView, UserView
from config import DATA_PATH
from contacts.models import Contact
from events.models import Event
from users.models import User


admin = Admin(
    templates_dir=str(DATA_PATH / "templates" / "admin"),
    auth_provider=AdminCredentialsProvider(),
    middlewares=[Middleware(SessionMiddleware, secret_key=config.SESSION_SECRET_KEY)]
)

admin.add_view(UserView(User, converter=MongoengineModelConverter(), icon="fa-solid fa-users"))
admin.add_view(ContactView(Contact, converter=MongoengineModelConverter(), icon="fa-solid fa-people-arrows"))
admin.add_view(EventView(Event, converter=MongoengineModelConverter(), icon="fa-solid fa-calendar-day"),)