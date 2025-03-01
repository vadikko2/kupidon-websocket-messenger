import cqrs

from service import unit_of_work
from service.requests.chats import get_chats


class GetChatsHandler(cqrs.RequestHandler[get_chats.GetChats, get_chats.Chats]):
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow

    @property
    def events(self):
        return self.uow.get_events()

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
                chats=[
                    get_chats.ChatInfo(
                        chat_id=chat.chat_id,
                        name=chat.name,
                        avatar=chat.avatar,
                        participants_count=chat.participants_count,
                        not_read_messages_count=chat.not_read_messages_count,
                        last_activity_timestamp=chat.last_activity_timestamp,
                        last_message_id=chat.last_message,
                    )
                    for chat in sorted_chats
                ],
            )
