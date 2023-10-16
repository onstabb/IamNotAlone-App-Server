from fastapi import APIRouter,  status, Depends, HTTPException, Request
from sse_starlette import EventSourceResponse

from contacts.service import get_contact_by_profile_ids
from messages import service, config
from messages.enums import MessageType

from messages.schemas import MessageOut, MessageIn, DialogItemOut
from messages.manager import notification_manager
from profiles import dependencies as profiles_dependencies
from profiles.models import Profile


router: APIRouter = APIRouter(tags=['Messages'], prefix="/messages")


@router.post("/send", response_model=MessageOut)
def send_message(message_in: MessageIn, profile: Profile = Depends(profiles_dependencies.get_active_profile)):

    contact = get_contact_by_profile_ids(profile.id, str(message_in.recipient_id))

    if not contact or not contact.is_established:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Contact must be established")

    other_profile: Profile = contact.initializer if contact.initializer == profile else contact.respondent
    messages_count = service.get_messages_count(profile, other_profile, message_type=MessageType.MESSAGE)

    if messages_count > config.MAX_SENT_MESSAGES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Limit of the messages has been exceeded")

    message = service.create_message(profile, other_profile, MessageType.MESSAGE, message_in.content_text)
    message_out = MessageOut.model_validate(message)
    notification_manager.send(message_out, recipient_id=other_profile.id)

    return message_out


@router.get("/chat/{profile_id}", response_model=list[MessageOut])
def get_chat(
    profile: Profile = Depends(profiles_dependencies.get_active_profile),
    other_profile: Profile = Depends(profiles_dependencies.get_active_profile_by_id)
):
    messages = service.get_chat(profile, other_profile, message_type=MessageType.MESSAGE)
    return messages


@router.get("/dialogs", response_model=list[DialogItemOut])
def get_dialogs(profile: Profile = Depends(profiles_dependencies.get_active_profile)):
    result = service.get_dialogs(profile)
    return result



@router.get("/listen")
async def receive_notifications(request: Request, profile: Profile = Depends(profiles_dependencies.get_active_profile)):
    return EventSourceResponse(notification_manager.retrieve_events(request, str(profile.id)))