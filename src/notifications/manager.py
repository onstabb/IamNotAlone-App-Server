import asyncio
from collections import deque
from typing import TypeVar

from fastapi import Request
from pydantic import BaseModel
from sse_starlette import ServerSentEvent

from models import PydanticObjectId
from notifications.enums import NotificationType

TBaseModel = TypeVar('TBaseModel', bound=BaseModel)


class ProfileNotificationManager:

    def __init__(self):
        self.clients: dict[str, deque[ServerSentEvent]] = dict()

    def connect(self, recipient_id: str) -> None:
        self.clients[recipient_id] = deque[ServerSentEvent]()

    def disconnect(self, recipient_id: str) -> None:
        del self.clients[recipient_id]

    def is_connected(self, recipient_id: str) -> bool:
        return self.clients.get(recipient_id) is not None

    async def retrieve_events(self, request: Request, recipient_id: str):
        self.connect(recipient_id)

        while True:
            if await request.is_disconnected():
                self.disconnect(recipient_id)
                break
            await asyncio.sleep(0.5)

            client_deque = self.clients[recipient_id]
            if len(client_deque) <= 0:
                continue
            notification = client_deque.pop()
            if not notification:
                continue
            yield notification

    def send(
        self, data: TBaseModel, recipient_id: PydanticObjectId | str, notification_type: NotificationType
    ) -> TBaseModel | None:

        recipient_id = str(recipient_id)
        if self.is_connected(recipient_id):
            self.clients[recipient_id].append(ServerSentEvent(data, event=notification_type))
            return data
        return None


notification_manager = ProfileNotificationManager()
