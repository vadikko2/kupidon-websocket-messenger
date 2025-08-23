import cqrs

from domain import chats
from service.interfaces import unit_of_work
from service.requests.chats import open_chat


class OpenChatHandler(cqrs.RequestHandler[open_chat.OpenChat, open_chat.ChatOpened]):
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow

    @property
    def events(self):
        return list(self.uow.get_events())

    async def handle(self, request: open_chat.OpenChat) -> open_chat.ChatOpened:
        new_chat = chats.Chat(
            initiator=request.initiator,
            name=request.name,
            avatar=request.avatar,
        )

        new_chat.add_participant(request.initiator, request.initiator)
        for participant in request.participants:
            new_chat.add_participant(participant, request.initiator)

        async with self.uow:
            await self.uow.chat_repository.add(new_chat)
            await self.uow.commit()

        return open_chat.ChatOpened(chat_id=new_chat.chat_id)
