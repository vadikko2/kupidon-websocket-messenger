import asyncio
import typing

import cqrs
import orjson

from domain import events
from infrastructure.brokers import messages_broker
from service import exceptions, unit_of_work


class TappingInChatHandler(cqrs.EventHandler[events.TappingInChat]):
    def __init__(self, uow: unit_of_work.UoW, broker: messages_broker.MessageBroker):
        self.uow = uow
        self.broker = broker

    async def handle(self, event: events.TappingInChat) -> None:
        async with self.uow:
            chat = await self.uow.chat_repository.get(event.chat_id)

            if chat is None:
                raise exceptions.ChatNotFound(event.chat_id)

            if not chat.is_participant(event.account_id):
                raise exceptions.ParticipantNotInChat(
                    event.account_id,
                    event.chat_id,
                )

            message_bytes: typing.ByteString = orjson.dumps(
                cqrs.NotificationEvent[events.TappingInChat](
                    event_name="TappingInChat",
                    payload=event,
                ).model_dump(mode="json"),
            )
            await asyncio.gather(
                *[
                    self.broker.send_message(receiver.account_id, message_bytes)
                    for receiver in chat.participants
                ],
            )
