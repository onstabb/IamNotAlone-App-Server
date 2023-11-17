import datetime

import factory
from factory import fuzzy


from contacts import service as contact_service
from contacts.models import Contact, Message, ContactState
from events.models import Event
from factories.helpers import build_json_dict
from location.database import geonames_db
from location.models import Location
from userprofile import config as profile_config
from userprofile.enums import Gender, ResidenceLength, ResidencePlan


from tests.factories import generators
from users.models import User, UserProfile


class _BaseMongoEngineFactory(factory.mongoengine.MongoEngineFactory):

    @classmethod
    def build_json_dict(cls, **kwargs) -> dict:
        return build_json_dict(cls, **kwargs)

    @classmethod
    def insert_many(cls, size, **kwargs) -> None:
        instances_built = cls.build_batch(size, **kwargs)
        cls._meta.model.objects.insert(instances_built, load_bulk=False)


class UserFactory(_BaseMongoEngineFactory):
    class Meta:
        model = User

    phone_number = factory.LazyFunction(generators.generate_random_mobile_number)
    password = factory.LazyFunction(generators.generate_hashed_password)
    profile = factory.SubFactory("tests.factories.factories.ProfileFactory",)
    photo_urls = factory.List([factory.Faker("image_url")])
    is_active = fuzzy.FuzzyChoice((False, False, False, True))

    class Params:
        active = factory.Trait(
            is_active=True,
            banned=False
        )




class LocationFactory(_BaseMongoEngineFactory):
    class Meta:
        model = Location

    city_id = factory.LazyFunction(lambda: generators.get_random_city().geonameid)
    current = factory.LazyAttribute(lambda location: geonames_db.get_city(location.city_id).coordinates)


class ProfileFactory(_BaseMongoEngineFactory):
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
    location = factory.SubFactory(LocationFactory)


class ContactFactory(_BaseMongoEngineFactory):
    class Meta:
        model = Contact

    initiator = factory.SubFactory(UserFactory)
    respondent = factory.SubFactory(UserFactory)
    initiator_state = factory.Iterator([contact for contact in ContactState] + [None])
    respondent_state = factory.Iterator([contact for contact in ContactState] + [None])
    status = factory.LazyAttribute(
        lambda contact: contact_service.get_contact_status(contact.initiator_state, contact.respondent_state)
    )

    class Params:

        active_dialog = factory.Trait(
            initiator_state=ContactState.ESTABLISHED,
            respondent_state=ContactState.ESTABLISHED,
            initiator__active=True,
            respondent__active=True,
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


class EventFactory(_BaseMongoEngineFactory):
    class Meta:
        model = Event

    title = factory.Faker("catch_phrase")
    description = factory.Faker("paragraph", nb_sentences=5)
    location = factory.SubFactory(LocationFactory, address=factory.Faker("address"))
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
