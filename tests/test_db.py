




#
# def test_candidate_search(user_factory):
#
#     from src.contacts import service
#     from src.geodata.models import City
#     from tests.factories.factories import ContactFactory, MessageFactory
#
#     user_factory.create_batch(20)
#     ContactFactory.create_batch(10)
#     MessageFactory.create_batch(10)
#
#     user = user_factory.create(
#         profile__gender_preference="any",
#         profile__current_city=City.objects[2],
#         profile__native_city=City.objects[3],
#     )
#
#     user_2 = user_factory.create(
#         profile__gender_preference="any",
#         profile__current_city=City.objects[4],
#         profile__native_city=City.objects[5],
#         profile__birthday=user.profile.birthday,
#     )
#
#
#     candidates = service.get_candidates(user.profile, 10)
#     print(user.profile.id, user.profile.current_city.id, user.profile.native_city.id)
#     import pprint
#     pprint.pprint(candidates)
#     # for candidate in candidates:
#     #     print(
#     #         calculate_distance(user.profile.coordinates['coordinates'], candidate.coordinates["coordinates"]),
#     #         candidate.current_city.name,
#     #         candidate.birthday
#     #     )
#
#
# def test_get_dialogs(user_factory):
#
#     from pprint import pprint
#
#
#     from src.messages import service as message_service
#     from src.profiles import models as profile_model
#     from tests.factories.factories import MessageFactory
#
#     user_factory.create_batch(10)
#     MessageFactory.create_batch(20)
#
#
#     dialogs = message_service.get_dialogs(profile_model.Profile.objects[0])
#
#     pprint(dialogs)