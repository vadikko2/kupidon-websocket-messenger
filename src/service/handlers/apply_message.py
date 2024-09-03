import cqrs

from domain import messages
from service import exceptions, unit_of_work
from service.commands import apply_message


class ApplyMessageReadHandler(
    cqrs.RequestHandler[apply_message.ApplyMessageRead, None],
):
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow
        self._events = []

    @property
    def events(self):
        return self._events

    async def handle(self, request: apply_message.ApplyMessageRead) -> None:
        async with self.uow:
            message = await self.uow.message_repository.get(request.message_id)
            if message is None:
                raise exceptions.MessageNotFound(request.message_id)

            chat = await self.uow.chat_repository.get(message.chat_id)
            if chat is None:
                raise exceptions.ChatNotFound(message.chat_id)

            if request.reader not in chat.participants:
                raise exceptions.ChangeStatusAccessDonated(
                    request.reader,
                    request.message_id,
                    messages.MessageStatus.READ,
                )

            message.read(request.reader)

            await self.uow.message_repository.update(message)
            await self.uow.commit()

        self._events += self.uow.get_events()


class ApplyMessageReceiveHandler(
    cqrs.RequestHandler[apply_message.ApplyMessageReceive, None],
):
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow
        self._events = []

    @property
    def events(self):
        return self._events

    async def handle(self, request: apply_message.ApplyMessageReceive) -> None:
        async with self.uow:
            message = await self.uow.message_repository.get(request.message_id)
            if message is None:
                raise exceptions.MessageNotFound(request.message_id)

            chat = await self.uow.chat_repository.get(message.chat_id)
            if chat is None:
                raise exceptions.ChatNotFound(message.chat_id)

            if request.receiver not in chat.participants:
                raise exceptions.ChangeStatusAccessDonated(
                    request.receiver,
                    request.message_id,
                    messages.MessageStatus.RECEIVED,
                )

            message.receive(request.receiver)

            await self.uow.message_repository.update(message)
            await self.uow.commit()

        self._events += self.uow.get_events()
