import cqrs

from domain import messages
from service import exceptions, unit_of_work
from service.requests import apply_message


class ApplyMessageHandler(
    cqrs.RequestHandler[apply_message.ApplyMessage, None],
):
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow
        self._events = []

    @property
    def events(self):
        return self._events

    async def handle(self, request: apply_message.ApplyMessage) -> None:
        async with self.uow:
            message = await self.uow.message_repository.get(request.message_id)

            if message is None or message.status == messages.MessageStatus.DELETED:
                raise exceptions.MessageNotFound(request.message_id)

            chat = await self.uow.chat_repository.get(message.chat_id)
            if chat is None:
                raise exceptions.ChatNotFound(message.chat_id)

            if request.applier not in chat.participants:
                raise exceptions.ChangeStatusAccessDonated(
                    request.applier,
                    request.message_id,
                    request.status,
                )

            if request.status == messages.MessageStatus.RECEIVED:
                message.receive(request.applier)

            elif request.status == messages.MessageStatus.READ:
                message.read(request.applier)

            await self.uow.message_repository.update(message)
            await self.uow.commit()

        self._events += self.uow.get_events()
