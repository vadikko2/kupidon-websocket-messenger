import logging

import cqrs

from service import exceptions
from service.interfaces import unit_of_work
from service.models.messages import delete_message
from service.validators import messages as message_validators

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
            if not message:
                raise exceptions.MessageNotFound(request.message_id)

            message_validators.raise_if_message_deleted(message)

            if request.deleter != message.sender:
                raise exceptions.MessageNotForAccount(message.message_id, request.deleter)

            message.delete()

            logger.debug(f"Message {request.message_id} deleted by {request.deleter}")

            await self.uow.message_repository.update(message)
            await self.uow.commit()
