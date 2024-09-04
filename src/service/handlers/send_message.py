import logging
import typing

import cqrs
from cqrs.events import event

from domain import messages
from service import exceptions, unit_of_work
from service.requests import send_message

logger = logging.getLogger(__name__)


class SendMessageHandler(
    cqrs.RequestHandler[send_message.SendMessage, send_message.MessageSent],
):
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow
        self._events = []

    @property
    def events(self) -> typing.List[event.Event]:
        return self._events

    async def handle(
        self,
        request: send_message.SendMessage,
    ) -> send_message.MessageSent:
        new_message = messages.Message(
            chat_id=request.chat_id,
            sender=request.sender,
            content=request.content,
            attachments=[
                messages.Attachment(
                    url=attachment.url,
                    name=attachment.name,
                    content_type=attachment.content_type,
                )
                for attachment in request.attachments
            ],
        )

        async with self.uow:
            chat = await self.uow.chat_repository.get(request.chat_id)

            if chat is None:
                raise exceptions.ChatNotFound(new_message.chat_id)

            if request.sender not in chat.participants:
                raise exceptions.ParticipantNotInChat(
                    request.sender,
                    chat.chat_id,
                )

            chat.add_message(new_message)

            await self.uow.message_repository.add(new_message)
            await self.uow.commit()

        self._events += self.uow.get_events()

        return send_message.MessageSent(
            message_id=new_message.message_id,
            created=new_message.created,
        )
