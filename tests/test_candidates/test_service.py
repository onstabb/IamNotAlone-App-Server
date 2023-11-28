from itertools import pairwise

from candidates import service
from users.enums import UserRole
from users.schemas import UserPublicOut


def test_get_candidates_for_user(user_factory):
    user_factory.create_batch(size=5)
    user = user_factory.create(profile__gender_preference=None)

    result = service.get_candidates_for_user(user, limit=5)

    for first, second in pairwise(result):
        assert first["profile"]["distance"] <= second["profile"]["distance"]

    for candidate in map(UserPublicOut.model_validate, result):
        candidate: UserPublicOut
        assert user.profile.gender == candidate.profile.gender_preference or not candidate.profile.gender_preference
        assert user.profile.gender_preference == candidate.profile.gender or not user.profile.gender_preference
        assert user.role not in UserRole.managers()

