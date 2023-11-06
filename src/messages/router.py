from fastapi import APIRouter, status, HTTPException

from contacts.service import get_contact_by_profile_ids
from messages import service, config

from messages.schemas import MessageOut, MessageIn
from notifications.enums import NotificationType
from notifications.manager import notification_manager
from profiles.dependencies import CurrentActiveProfileByToken, ActiveTargetProfileById
from profiles.models import Profile


router: APIRouter = APIRouter()


@router.post("", response_model=MessageOut)
def send_message(message_in: MessageIn, profile: CurrentActiveProfileByToken):

    contact = get_contact_by_profile_ids(profile.id, str(message_in.recipient_id))

    if not contact or not contact.is_established:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Contact must be established")

    target_profile: Profile = contact.initiator if contact.initiator == profile else contact.respondent
    messages_count = service.get_messages_count(profile, target_profile)

    if messages_count > config.MAX_SENT_MESSAGES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Limit of the messages has been exceeded")

    message_out = MessageOut.model_validate(
        service.create_message(profile, target_profile, message_in.content_text)
    )
    notification_manager.send(message_out, recipient_id=target_profile.id, notification_type=NotificationType.MESSAGE)
    return message_out


@router.get("", response_model=list[MessageOut])
def get_messages(current_profile: CurrentActiveProfileByToken, target_profile: ActiveTargetProfileById, ):
    messages = service.get_chat(current_profile, target_profile)
    return messages


@router.get("/dialogs", response_model=list[MessageOut])
def get_dialogs(current_profile: CurrentActiveProfileByToken):
    result = service.get_dialogs(current_profile)
    return result
