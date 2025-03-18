import logging

import cqrs

from service import exceptions, unit_of_work
from service.requests.messages import delete_message

logger = logging.getLogger(__name__)


class DeleteMessageHandler(cqrs.RequestHandler[delete_message.DeleteMessage, None]):
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow

    @property
    def events(self):
        return list(self.uow.get_events())

    async def handle(self, request: delete_message.DeleteMessage) -> None:
        async with self.uow:
            message = await self.uow.message_repository.get(request.message_id)
            if message is None or message.deleted:
                raise exceptions.MessageNotFound(request.message_id)

            if request.deleter != message.sender:
                raise exceptions.ParticipantNotInChat(request.deleter, message.chat_id)

            message.delete()

            logger.debug(f"Message {request.message_id} deleted by {request.deleter}")

            await self.uow.message_repository.update(message)
            await self.uow.commit()
