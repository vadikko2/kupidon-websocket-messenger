import logging

import cqrs

from service import exceptions
from service.interfaces import unit_of_work
from service.models.chats import set_first_writer
from service.validators import chats as chats_validators

logger = logging.getLogger(__name__)


class SetFirstWriterHandler(cqrs.RequestHandler[set_first_writer.SetFirstWriter, None]):
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow

    @property
    def events(self):
        return []

    async def handle(self, request: set_first_writer.SetFirstWriter) -> None:
        async with self.uow:
            chat = await self.uow.chat_repository.get(request.chat_id)
            if chat is None:
                raise exceptions.ChatNotFound(request.chat_id)

            chats_validators.raise_if_sender_not_in_chat(chat, request.chat_id, request.account_id)

            participant = chat.is_participant(request.account_id)
            participant.set_first_writer(request.first_writer)  # pyright: ignore[reportOptionalMemberAccess]

            await self.uow.chat_repository.update(chat)
            await self.uow.commit()
        logger.info(
            "Set first writer for account#{} in chat#{} to value#{}".format(
                request.account_id,
                request.chat_id,
                request.first_writer,
            ),
        )
