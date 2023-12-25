from fastapi import APIRouter, HTTPException, status, Query

from contacts import config, service
from contacts.enums import ContactState, ContactUpdateAction, ContactType
from contacts.models import Contact
from contacts.schemas import ContactUpdateIn, ContactCreateDataIn, ContactOut, MessageIn, MessageOut
from notifications.enums import NotificationType
from notifications.manager import notification_manager
from users.dependencies import CurrentActiveCompletedUser, TargetActiveCompletedUser, get_active_completed_user
from users.schemas import UserPublicOut


router = APIRouter()


@router.get("", response_model=list[ContactOut])
def get_contacts(
        current_user: CurrentActiveCompletedUser,
        contact_type: ContactType = Query(alias="contactType"),
        limit: int = 0,
):
    if contact_type == ContactType.LIKE:
        return service.get_contacts_by_user(
            current_user, limit=limit, status=None, initiator_state=ContactState.ESTABLISHED, respondent=current_user.id
        )
    # if contact_type == ContactType.DIALOG
    return service.get_contacts_by_user(current_user, limit=limit, status=ContactState.ESTABLISHED)


@router.get("/{user_id}", response_model=ContactOut)
def get_contact(current_user: CurrentActiveCompletedUser, target_user: TargetActiveCompletedUser):
    contact = service.get_contact_by_users_pair(current_user, target_user)
    contact.reset_current_user(current_user)
    return contact


@router.post("", response_model=ContactOut, status_code=status.HTTP_201_CREATED)
def create_contact(data_in: ContactCreateDataIn, current_user: CurrentActiveCompletedUser):
    if data_in.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create contact with yourself",
        )

    target_user = get_active_completed_user(data_in.user_id)
    contact: Contact | None = service.get_contact_by_users_pair(current_user, target_user)
    if contact:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"Contact with profile `{target_user.id}` already exists"
        )

    contact = service.create_contact_by_initiator(initiator=current_user, respondent=target_user, data_in=data_in)
    if data_in.state == ContactState.ESTABLISHED:
        notification_manager.put_notification(
            UserPublicOut.model_validate(current_user, from_attributes=True),
            target_user.id,
            NotificationType.LIKE
        )
    contact.reset_current_user(current_user)
    return contact


@router.patch("/{user_id}", response_model=ContactOut)
def update_contact(
        target_user: TargetActiveCompletedUser,
        current_user: CurrentActiveCompletedUser,
        update_data: ContactUpdateIn,
):
    contact = service.get_contact_by_users_pair(current_user, target_user)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact doesn't exists")

    if contact.status == ContactState.BLOCKED:
        return contact

    if contact.status and update_data.action not in (ContactUpdateAction.BLOCK, ContactUpdateAction.SEEN):
        return contact

    service.update_contact(update_data.action, current_user, contact)
    if update_data.action == ContactUpdateAction.ESTABLISH and contact.established and current_user == contact.respondent:
        notification_manager.put_notification(
            UserPublicOut.model_validate(current_user, from_attributes=True),
            recipient_id=contact.initiator,
            notification_type=NotificationType.CONTACT_ESTABLISHED
        )
    contact.reset_current_user(current_user)
    return contact


@router.post("/{user_id}/messages", response_model=MessageOut)
def send_message(
        message_in: MessageIn,
        current_user: CurrentActiveCompletedUser,
        target_user: TargetActiveCompletedUser,
):
    contact = service.get_contact_by_users_pair(current_user, target_user)
    if not contact or not contact.established:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Contact must be established")

    if service.get_messages_count_from_sender(contact, current_user) >= config.MAX_SENT_MESSAGES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Limit of the messages is exceeded")

    message = service.create_message(contact, sender=current_user, message_in=message_in)
    message_out = MessageOut.model_validate(message, from_attributes=True)
    notification_manager.put_notification(
        message_out, recipient_id=target_user.id, notification_type=NotificationType.MESSAGE
    )
    return message_out
