from contacts import service
from contacts.enums import ContactState
from contacts.schemas import ContactCreateDataIn, ContactOut


def test_create_contact(user_factory):
    first_user, second_user = user_factory.create(), user_factory.create()

    contact = service.create_contact_by_initiator(
        first_user, second_user, ContactCreateDataIn(state=ContactState.ESTABLISHED, user_id=second_user.id)
    )

    assert contact.initiator == first_user
    assert contact.respondent == second_user


def test_get_contacts_for_user(contact_factory):
    contact = contact_factory.create(active_dialog=True)

    found_contacts = [
        ContactOut.model_validate(document)
        for document in service.get_contacts_by_user(contact.initiator, status=ContactState.ESTABLISHED)
    ]

    for contact_out in found_contacts:
        if contact.respondent.id == contact_out.opposite_user.id and contact.status == contact_out.status:
            break
    else:
        raise AssertionError


def test_get_contact_by_user_pair(contact_factory):
    contact = contact_factory(active_dialog=True)
    current_user, target_user = contact.initiator, contact.respondent

    found_contact = service.get_contact_by_users_pair(current_user, target_user)

    assert found_contact == contact
    assert found_contact.initiator == current_user
    assert found_contact.respondent == target_user


def test_get_messages_count(contact_factory):
    contact = contact_factory(active_dialog=True)
    count = service.get_messages_count_from_sender(contact, contact.initiator)
    assert count > 0
