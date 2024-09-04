import typing
import uuid

import cqrs
from cqrs.events import event

from domain import messages
from service import exceptions, unit_of_work
from service.requests import get_history


class GetHistoryHandler(
    cqrs.RequestHandler[get_history.GetHistory, get_history.History],
):
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow

    @property
    def events(self) -> list[event.Event]:
        return []

    async def mark_message_as_delivered(
        self,
        account: typing.Text,
        message_id: uuid.UUID,
    ) -> None:
        message = await self.uow.message_repository.get(message_id)

        if message is None:
            raise exceptions.MessageNotFound(message_id)

        chat = await self.uow.chat_repository.get(message.chat_id)
        if chat is None:
            raise exceptions.ChatNotFound(message.chat_id)

        if account not in chat.participants:
            raise exceptions.ChangeStatusAccessDonated(
                account,
                message_id,
                messages.MessageStatus.DELIVERED,
            )

        message.deliver(account)
        await self.uow.message_repository.update(message)

    async def handle(self, request: get_history.GetHistory) -> get_history.History:
        async with self.uow:
            chat_history = await self.uow.chat_repository.get_chat_history(
                chat_id=request.chat_id,
                messages_limit=request.messages_limit,
                latest_message_id=request.latest_message_id,
            )

            if chat_history is None:
                raise exceptions.ChatNotFound(request.chat_id)

            if request.account not in chat_history.participants:
                raise exceptions.ParticipantNotInChat(
                    request.account,
                    chat_history.chat_id,
                )

            for message in chat_history.history:
                if request.account in chat_history.participants:
                    await self.mark_message_as_delivered(
                        request.account,
                        message.message_id,
                    )

            await self.uow.commit()

        return get_history.History(messages=chat_history.history)
