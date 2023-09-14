from json import JSONDecodeError

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool


from contacts.service import get_contact_by_profile_ids
from messages import service, config
from messages.enums import MessageType
from messages.notificationmanager import notification_manager
from messages.schemas import MessageOut, MessageIn, DialogItemOut
from profiles import dependencies as profiles_dependencies
from profiles import service as profile_service
from profiles.models import Profile
from security import WebSocketJWTBearer

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

    return notification_manager.create_and_send_message(
        profile, other_profile, MessageType.MESSAGE, content_text=message_in.content_text
    )


@router.get("/chat/{profile_id}", response_model=list[MessageOut])
def get_chat(
    profile: Profile = Depends(profiles_dependencies.get_active_profile),
    other_profile: Profile = Depends(profiles_dependencies.get_active_profile_by_id)
):
    messages = service.get_chat(profile, other_profile, message_type=MessageType.MESSAGE)
    return messages


@router.get("/dialogs", response_model=list[DialogItemOut])
def get_dialogs(profile: Profile = Depends(profiles_dependencies.get_active_profile)):
    return service.get_dialogs(profile)


@router.websocket_route("/listen")
async def websocket_endpoint(websocket: WebSocket) -> None:
    profile = await run_in_threadpool(profile_service.get_active_profile, profile_id=WebSocketJWTBearer(websocket))
    if not profile:
        raise WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION, reason="Profile does not exists or disabled")

    await notification_manager.connect(websocket, profile_id=profile.id)
    try:
        while True:
            try:
                data: dict = await websocket.receive_json(mode="text")
            except JSONDecodeError:
                continue

            message_id = data.get("received_message_id")
            if not message_id:
                continue

            await run_in_threadpool(
                service.set_message_as_delivered_by_id, message_id=message_id, recipient_id=profile.id
            )

    except WebSocketDisconnect:
        await websocket.close()
        notification_manager.disconnect(profile_id=profile.id)



