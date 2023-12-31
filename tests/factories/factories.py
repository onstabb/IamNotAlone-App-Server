import datetime

import factory
from factory import fuzzy

from authorization.models import User
from contacts import service as contact_service
from contacts.models import ProfileContact, ContactState
from messages.models import Message, MessageType
from profiles import config as profile_config
from profiles.enums import Gender, ResidenceLength, ResidencePlan
from profiles.models import Profile

from tests.factories import generators


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


class ProfileFactory(factory.mongoengine.MongoEngineFactory):
    class Meta:
        model = Profile

    name = factory.Faker("user_name")
    birthday = fuzzy.FuzzyDate(
        start_date=datetime.date.today() - datetime.timedelta(days=365 * profile_config.MAX_AGE),
        end_date=datetime.date.today() - datetime.timedelta(days=365 * profile_config.MIN_AGE),
    )
    current_city = factory.LazyFunction(generators.create_random_city)
    native_city = factory.LazyFunction(generators.create_random_city)
    coordinates = factory.LazyAttribute(lambda self: self.current_city.coordinates)
    gender = factory.Iterator(Gender)
    gender_preference = factory.Iterator([None] + [gender for gender in Gender])
    description = factory.Faker("paragraph", nb_sentences=2)
    residence_plan = factory.Iterator(ResidencePlan)
    residence_length = factory.Iterator(ResidenceLength)
    photo_urls = factory.List([factory.Faker("image_url")])

    disabled = fuzzy.FuzzyChoice((True, True, True, False))


class ContactFactory(factory.mongoengine.MongoEngineFactory):

    class Meta:
        model = ProfileContact

    initializer = factory.Iterator(Profile.objects[:1])
    respondent = factory.Iterator(Profile.objects[1:])
    initializer_state = factory.Iterator([contact for contact in ContactState] + [None])
    respondent_state = factory.Iterator([contact for contact in ContactState] + [None])
    status = factory.LazyAttribute(
        lambda contact: contact_service.get_contact_status(contact.initializer_state, contact.respondent_state)
    )



class MessageFactory(factory.mongoengine.MongoEngineFactory):

    class Meta:
        model = Message

    content_text = factory.Faker("paragraph", nb_sentences=4)
    sender = factory.Iterator(Profile.objects[:1])
    recipient = factory.Iterator(Profile.objects[1:])
    message_type = MessageType.MESSAGE
    delivered = True
    has_read = fuzzy.FuzzyChoice((True, False))