import datetime

import factory
from factory import fuzzy

from contacts.models import Contact, Message, ContactState
from events.models import Event
from location.database import geonames_db
from reports.enums import ReportType
from reports.models import Report
from userprofile import config as profile_config
from userprofile.enums import Gender, ResidenceLength, ResidencePlan
from tests.factories import generators
from users.models import User, UserProfile


class _BaseMongoEngineFactory(factory.mongoengine.MongoEngineFactory):

    @classmethod
    def build_json_dict(cls, **kwargs) -> dict:
        result: dict = factory.build(dict, FACTORY_CLASS=cls, **kwargs)
        for key, value in cls.__dict__.items():
            if isinstance(value, factory.SubFactory):
                result[key] = value.get_factory().build_json_dict()

        for key, value in result.items():
            if isinstance(value, datetime.date):
                result[key] = value.isoformat()

        return result


class _UsingLocationFactory(_BaseMongoEngineFactory):
    city_id = factory.LazyFunction(lambda: generators.get_random_city().geonameid)
    location = factory.LazyAttribute(lambda location: geonames_db.get_city(location.city_id).coordinates)


class UserFactory(_BaseMongoEngineFactory):
    class Meta:
        model = User

    phone_number = factory.LazyFunction(generators.generate_random_mobile_number)
    password = factory.LazyFunction(generators.generate_hashed_password)
    profile = factory.SubFactory("tests.factories.factories.ProfileFactory",)
    photo_urls = factory.List([factory.Faker("image_url"), factory.Faker("image_url")])
    is_active = True
    banned = False


class ProfileFactory(_UsingLocationFactory):
    class Meta:
        model = UserProfile

    name = factory.Faker("user_name")
    birthdate = fuzzy.FuzzyDate(
        start_date=datetime.date.today() - datetime.timedelta(days=365 * profile_config.MAX_AGE),
        end_date=datetime.date.today() - datetime.timedelta(days=365 * profile_config.MIN_AGE),
    )

    gender = factory.Iterator(Gender)
    gender_preference = factory.Iterator([None] + [gender for gender in Gender])
    description = factory.Faker("paragraph", nb_sentences=2)
    residence_plan = factory.Iterator(ResidencePlan)
    residence_length = factory.Iterator(ResidenceLength)


class ContactFactory(_BaseMongoEngineFactory):
    class Meta:
        model = Contact

    initiator = factory.SubFactory(UserFactory)
    respondent = factory.SubFactory(UserFactory)
    initiator_state = factory.Iterator([contact for contact in ContactState] + [None])
    respondent_state = factory.Iterator([contact for contact in ContactState] + [None])

    class Params:
        active_dialog = factory.Trait(
            initiator_state=ContactState.ESTABLISHED,
            respondent_state=ContactState.ESTABLISHED,
            messages=factory.List(
                [
                    factory.SubFactory(
                        'tests.factories.factories.MessageFactory',
                        sender=factory.SelfAttribute(f"...{sender}")
                    )
                    for sender in ("initiator", "respondent", "initiator", "initiator")
                ]
            )
        )

        likes = factory.Trait(
            initiator_state=ContactState.ESTABLISHED,
            respondent_state=None,
        )


class MessageFactory(_BaseMongoEngineFactory):
    class Meta:
        model = Message

    text = factory.Faker("paragraph", nb_sentences=4)


class EventFactory(_UsingLocationFactory):
    class Meta:
        model = Event

    title = factory.Faker("catch_phrase")
    description = factory.Faker("paragraph", nb_sentences=5)
    address = factory.Faker("address")
    start_at = factory.Faker("date_time_this_decade")
    image_urls = factory.List([factory.Faker("image_url"), factory.Faker("image_url"), factory.Faker("image_url"),])

    @factory.post_generation
    def subscribers(self: Event, create: bool, extracted: list[User] | None, **kwargs) -> None:
        if not create:
            return

        if extracted is None:
            users: list[User] = UserFactory.create_batch(kwargs.pop("size", 1), events=[self], **kwargs)
        else:
            users = extracted

        self.subscribers.extend(users)
        self.save()


class ReportFactory(_BaseMongoEngineFactory):
    class Meta:
        model = Report

    initiator = factory.SubFactory(UserFactory)
    respondent = factory.SubFactory(UserFactory)
    type = factory.Iterator(ReportType)
    additional_info = factory.Faker("paragraph", nb_sentences=5)
