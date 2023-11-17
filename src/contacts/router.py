from fastapi import APIRouter, HTTPException, status, Query

from contacts import config, service
from contacts.enums import ContactState
from contacts.models import Contact
from contacts.schemas import ContactStateIn, ContactCreateDataIn, ContactOut, MessageIn, MessageOut
from notifications.enums import NotificationType
from notifications.manager import notification_manager
from users.dependencies import CurrentActiveCompletedUser, TargetActiveCompletedUser, get_active_completed_user
from users.schemas import UserPublicOut


router = APIRouter()


@router.get("", response_model=list[ContactOut])
def get_contacts(
        current_user: CurrentActiveCompletedUser,
        contact_status: ContactState = Query(alias="status", default=ContactState.ESTABLISHED),
        limit: int = 0,
):
    return service.get_contacts_for_user(current_user, limit=limit, status=contact_status)


@router.get("/{user_id}", response_model=ContactOut)
def get_contact(current_user: CurrentActiveCompletedUser, target_user: TargetActiveCompletedUser):
    return service.get_contact_by_users_pair(current_user, target_user)


@router.post("", response_model=ContactOut, status_code=status.HTTP_201_CREATED)
def create_contact(data_in: ContactCreateDataIn, current_user: CurrentActiveCompletedUser):

    if data_in.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You cannot create contact with yourself",
        )

    target_user = get_active_completed_user(data_in.user_id)
    contact: Contact | None = service.get_contact_by_users_pair(current_user.id, target_user.id)

    if contact:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"Contact with profile `{target_user.id}` already exists"
        )

    contact = service.create_contact_by_initiator(current_user, target_user, data_in)

    if data_in.action == ContactState.ESTABLISHED:
        notification_manager.send(
            UserPublicOut.model_validate(current_user, from_attributes=True),
            target_user.id,
            NotificationType.LIKE
        )

    return contact


@router.patch("/{user_id}", response_model=ContactOut)
def update_contact_state(
        target_user: TargetActiveCompletedUser,
        current_user: CurrentActiveCompletedUser,
        state_data: ContactStateIn,
):
    contact = service.get_contact_by_users_pair(current_user.id, target_user.id)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact doesn't exists")

    if contact.status == ContactState.BLOCKED or (contact.status and state_data.action != ContactState.BLOCKED):
        return contact

    service.update_contact_status(state_data, current_user, contact)
    if contact.established and current_user == contact.respondent:
        notification_manager.send(
            UserPublicOut.model_validate(current_user, from_attributes=True),
            contact.initiator,
            NotificationType.CONTACT_ESTABLISHED
        )

    return contact


@router.post("/{user_id}/messages", response_model=MessageOut)
def send_message(
        message_in: MessageIn,
        current_user: CurrentActiveCompletedUser,
        target_user: TargetActiveCompletedUser,
):
    contact = service.get_contact_by_users_pair(current_user.id, target_user.id)
    if not contact or not contact.established:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Contact must be established")

    if service.get_messages_count_from_sender(contact, current_user) > config.MAX_SENT_MESSAGES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Limit of the messages has been exceeded")

    message = service.create_message(contact, sender=current_user, message_in=message_in)
    message_out = MessageOut.model_validate(message)
    notification_manager.send(message_out, recipient_id=target_user.id, notification_type=NotificationType.MESSAGE)
    return message_out
