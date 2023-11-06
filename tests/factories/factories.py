import datetime

import factory
from factory import fuzzy

from authorization.models import User
from contacts import service as contact_service
from contacts.models import ProfileContact, ContactState
from geodata.models import Location
from messages.models import Message
from profiles import config as profile_config
from profiles.enums import Gender, ResidenceLength, ResidencePlan
from profiles.models import Profile

from tests.factories import generators
from tests.factories.helpers import Objects


class UserFactory(factory.mongoengine.MongoEngineFactory,):
    class Meta:
        model = User

    phone_number = factory.LazyFunction(generators.generate_random_mobile_number)
    password = factory.LazyFunction(generators.generate_hashed_password)
    profile = factory.SubFactory("tests.factories.factories.ProfileFactory",)

    @classmethod
    def insert_many(cls, size, **kwargs) -> None:
        instances_built = cls.build_batch(size, **kwargs)

        Profile.objects.insert([user.profile for user in instances_built], load_bulk=False)
        cls._meta.model.objects.insert(instances_built, load_bulk=False)


class LocationFactory(factory.mongoengine.MongoEngineFactory):
    class Meta:
        model = Location

    city_coordinates = factory.LazyFunction(lambda: generators.get_random_city().coordinates)
    coordinates = factory.SelfAttribute("city_coordinates")


class ProfileFactory(factory.mongoengine.MongoEngineFactory):
    class Meta:
        model = Profile

    name = factory.Faker("user_name")
    birthday = fuzzy.FuzzyDate(
        start_date=datetime.date.today() - datetime.timedelta(days=365 * profile_config.MAX_AGE),
        end_date=datetime.date.today() - datetime.timedelta(days=365 * profile_config.MIN_AGE),
    )
    current_city_id = factory.LazyFunction(lambda: generators.get_random_city().geonameid)
    native_city_id = factory.LazyFunction(lambda: generators.get_random_city().geonameid)

    gender = factory.Iterator(Gender)
    gender_preference = factory.Iterator([None] + [gender for gender in Gender])
    description = factory.Faker("paragraph", nb_sentences=2)
    residence_plan = factory.Iterator(ResidencePlan)
    residence_length = factory.Iterator(ResidenceLength)
    photo_urls = factory.List([factory.Faker("image_url")])

    location = factory.SubFactory(LocationFactory)
    disabled = fuzzy.FuzzyChoice((False, False, False, True))


class ContactFactory(factory.mongoengine.MongoEngineFactory):

    class Meta:
        model = ProfileContact

    initiator = factory.Iterator(Objects(Profile, slice(1)))
    respondent = factory.Iterator(Objects(Profile, slice(1, None)))
    initiator_state = factory.Iterator([contact for contact in ContactState] + [None])
    respondent_state = factory.Iterator([contact for contact in ContactState] + [None])
    status = factory.LazyAttribute(
        lambda contact: contact_service.get_contact_status(contact.initiator_state, contact.respondent_state)
    )



class MessageFactory(factory.mongoengine.MongoEngineFactory):

    class Meta:
        model = Message

    content_text = factory.Faker("paragraph", nb_sentences=4)
    sender = factory.Iterator(Objects(Profile, slice(1)))
    recipient = factory.Iterator(Objects(Profile, slice(1, None)))
    has_read = fuzzy.FuzzyChoice((True, False))