import typing

import cqrs
from cqrs.events import event

from domain import chats
from service import unit_of_work
from service.commands import open_chat


class OpenChatHandler(cqrs.RequestHandler[open_chat.OpenChat, open_chat.ChatOpened]):
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow
        self._events = []

    @property
    def events(self) -> typing.List[event.Event]:
        return self._events

    async def handle(self, request: open_chat.OpenChat) -> open_chat.ChatOpened:
        new_chat = chats.Chat(
            initiator=request.initiator,
            participants=[request.initiator] + request.participants,
            name=request.name,
        )
        async with self.uow:
            await self.uow.chat_repository.add(new_chat)
            await self.uow.commit()

        return open_chat.ChatOpened(chat_id=new_chat.chat_id)
