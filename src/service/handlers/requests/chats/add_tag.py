import cqrs
from cqrs.events import event

from domain import exceptions as domain_exceptions, participants
from service import exceptions
from service.interfaces import unit_of_work
from service.models.chats import add_tag
from service.validators import chats as chat_validators


class AddTagHandler(cqrs.RequestHandler[add_tag.AddTag, None]):
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow

    @property
    def events(self) -> list[event.Event]:
        return list(self.uow.get_events())

    async def handle(self, request: add_tag.AddTag) -> None:
        async with self.uow:
            chat = await self.uow.chat_repository.get(request.chat_id)
            if chat is None:
                raise exceptions.ChatNotFound(request.chat_id)
            chat_validators.raise_if_sender_not_in_chat(
                chat,
                request.chat_id,
                request.account_id,
            )

            try:
                chat.add_tag(
                    request.account_id,
                    participants.ChatTag(tag=request.tag),
                )

            except domain_exceptions.ParticipantNotInChat:
                raise exceptions.ParticipantNotInChat(
                    request.account_id,
                    request.chat_id,
                )
            await self.uow.chat_repository.update(chat)
            await self.uow.commit()
