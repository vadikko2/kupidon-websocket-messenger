import typing

import cqrs
from cqrs.events import event

from domain import chats
from service import exceptions, unit_of_work
from service.requests.chats import delete_chat


class DeleteChatHandler(cqrs.RequestHandler[delete_chat.DeleteChat, None]):
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow

    @property
    def events(self) -> typing.List[event.Event]:
        return []

    async def handle(self, request: delete_chat.DeleteChat) -> None:
        async with self.uow:
            chat: chats.Chat | None = await self.uow.chat_repository.get(
                request.chat_id,
            )
            if not chat:
                raise exceptions.ChatNotFound(request.chat_id)

            if not chat.is_participant(request.actor):
                raise exceptions.ParticipantNotInChat(
                    request.actor,
                    request.chat_id,
                )

            chat.delete_for(request.actor)

            await self.uow.chat_repository.update(chat)
            await self.uow.commit()
