import asyncio
import typing

import cqrs
import orjson

from domain import events
from infrastructure.brokers import messages_broker
from service import exceptions
from service.interfaces import unit_of_work
from service.validators import chats as chat_validators


class TappingInChatHandler(cqrs.EventHandler[events.TappingInChat]):
    def __init__(self, uow: unit_of_work.UoW, broker: messages_broker.MessageBroker):
        self.uow = uow
        self.broker = broker

    async def handle(self, event: events.TappingInChat) -> None:
        async with self.uow:
            chat = await self.uow.chat_repository.get(event.chat_id)
            if chat is None:
                raise exceptions.ChatNotFound(event.chat_id)
            chat_validators.raise_if_sender_not_in_chat(chat, event.chat_id, event.account_id)

            message_bytes: typing.ByteString = orjson.dumps(
                cqrs.NotificationEvent[events.TappingInChat](
                    event_name="TappingInChat",
                    payload=event,
                ).model_dump(mode="json"),
            )
            await asyncio.gather(
                *[self.broker.send_message(receiver.account_id, message_bytes) for receiver in chat.participants],
            )
