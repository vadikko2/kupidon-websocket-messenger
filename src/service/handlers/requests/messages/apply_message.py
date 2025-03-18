import cqrs

from service import exceptions, unit_of_work
from service.requests.messages import apply_message


class ApplyMessageHandler(
    cqrs.RequestHandler[apply_message.ApplyMessage, None],
):
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow

    @property
    def events(self):
        return list(self.uow.get_events())

    async def handle(self, request: apply_message.ApplyMessage) -> None:
        async with self.uow:
            # Достаем сообщение
            message = await self.uow.message_repository.get(request.message_id)

            if message is None or message.deleted:
                raise exceptions.MessageNotFound(request.message_id)

            chat = await self.uow.chat_repository.get(message.chat_id)
            if chat is None:
                raise exceptions.ChatNotFound(message.chat_id)

            if not chat.is_participant(request.applier):
                raise exceptions.ParticipantNotInChat(
                    request.applier,
                    message.chat_id,
                )

            # Проверяем что последнее прочитанное не позже чем текущее
            last_read = await self.uow.read_message_repository.last_read(
                request.applier,
                message.chat_id,
            )
            if last_read is not None and last_read.message.created >= message.created:
                return

            read_message = chat.read_message(request.applier, message)
            if read_message is not None:
                await self.uow.read_message_repository.register(read_message)

            await self.uow.chat_repository.update(chat)
            await self.uow.commit()
