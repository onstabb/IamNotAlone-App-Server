from fastapi import WebSocket

from messages import service
from messages.enums import MessageType
from messages.schemas import MessageOut
from models import PydanticObjectId
from profiles.models import Profile


class _NotificationManager:
    def __init__(self) -> None:
        self._active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, profile_id: PydanticObjectId | str) -> None:
        await websocket.accept()
        self._active_connections[str(profile_id)] = websocket

    def disconnect(self, profile_id: PydanticObjectId | str) -> None:
        del self._active_connections[str(profile_id)]

    def create_and_send_message(
            self,
            sender: Profile,
            recipient: Profile,
            message_type: MessageType,
            content_text: str | None
    ) -> MessageOut:
        message = service.create_message(sender, recipient, message_type, content_text)
        message_out: MessageOut = MessageOut.model_validate(message)
        # asyncio.to_thread(asyncio.run, self.send_message(message_out))
        return message_out

    async def send_message(self, message_out: MessageOut) -> None:

        try:
            await self._active_connections[str(message_out.recipient.id)].send_json(message_out.model_dump_json())
        except IndexError:
            pass


notification_manager: _NotificationManager = _NotificationManager()
