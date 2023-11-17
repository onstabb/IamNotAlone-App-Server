from contacts.enums import ContactState
from likes import service


def test_get_likes(contact_factory, user):
    contact_factory.create_batch(5, likes=True, respondent=user)

    contacts = service.get_likes(user)

    for contact in contacts:
        assert contact.initiator != user
        assert contact.initiator_state == ContactState.ESTABLISHED
        assert contact.respondent_state is None
        assert contact.status is None
