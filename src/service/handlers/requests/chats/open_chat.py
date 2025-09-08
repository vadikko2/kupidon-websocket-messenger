import cqrs

from domain import chats, messages
from service.interfaces import unit_of_work
from service.models.chats import open_chat


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
        first_writers = set(request.first_writers or [])
        # set initiator as first_writer if specified
        if request.initiator in first_writers:
            p = new_chat.is_participant(request.initiator)
            if p is not None:
                p.set_first_writer(True)
        for participant in request.participants:
            new_chat.add_participant(participant, request.initiator)
            if participant in first_writers:
                p = new_chat.is_participant(participant)
                if p is not None:
                    p.set_first_writer(True)

        async with self.uow:
            await self.uow.chat_repository.add(new_chat)
            if request.welcome_message is not None:
                new_message = messages.Message(
                    chat_id=new_chat.chat_id,
                    sender=request.initiator,
                    content=request.welcome_message,
                )
                await self.uow.message_repository.add(new_message)
                new_chat.add_message(new_message)

            await self.uow.commit()

        return open_chat.ChatOpened(chat_id=new_chat.chat_id)
