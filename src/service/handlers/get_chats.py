import cqrs
from cqrs.events import event

from service import unit_of_work
from service.requests import get_chats


class GetChatsHandler(cqrs.RequestHandler[get_chats.GetChats, get_chats.Chats]):
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow
        self._events = []

    @property
    def events(self) -> list[event.Event]:
        return self._events

    async def handle(self, request: get_chats.GetChats) -> get_chats.Chats:
        async with self.uow:
            chats = await self.uow.chat_repository.get_all(
                participant=request.participant,
            )
            sorted_chats = sorted(
                chats,
                key=lambda x: x.last_activity_timestamp,
                reverse=True,
            )
            return get_chats.Chats(
                chats=sorted_chats[request.offset : request.offset + request.limit],
            )
