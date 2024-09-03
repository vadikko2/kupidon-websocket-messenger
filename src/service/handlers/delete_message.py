import logging

import cqrs

from domain import messages
from service import exceptions, unit_of_work
from service.commands import delete_message

logger = logging.getLogger(__name__)


class DeleteMessageHandler(cqrs.RequestHandler[delete_message.DeleteMessage, None]):
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow
        self._events = []

    @property
    def events(self):
        return self._events

    async def handle(self, request: delete_message.DeleteMessage) -> None:
        async with self.uow:
            message = await self.uow.message_repository.get(request.message_id)
            if message is None:
                raise exceptions.MessageNotFound(request.message_id)

            chat = await self.uow.chat_repository.get(message.chat_id)
            if chat is None:
                raise exceptions.ChatNotFound(message.chat_id)

            if request.deleter not in chat.participants:
                raise exceptions.ChangeStatusAccessDonated(
                    request.deleter,
                    request.message_id,
                    messages.MessageStatus.DELETED,
                )

            message.delete()

            logger.debug(f"Message {request.message_id} deleted by {request.deleter}")

            await self.uow.message_repository.update(message)
            await self.uow.commit()

        self._events += self.uow.get_events()
