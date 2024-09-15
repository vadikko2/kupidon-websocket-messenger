import asyncio
import logging
import typing

import cqrs
import orjson

from domain import events as domain_events
from infrastructure.brokers import protocol as broker_protocol
from service import events as notification_events, exceptions, unit_of_work

logger = logging.getLogger(__name__)


class NewMessageAddedHandler(cqrs.EventHandler[domain_events.NewMessageAdded]):
    """
    Sends message to broker for all receivers.
    """

    def __init__(self, uow: unit_of_work.UoW, broker: broker_protocol.MessageBroker):
        self.uow = uow
        self.broker = broker

    async def send_to_receiver(self, message: bytes, receiver: typing.Text) -> None:
        try:
            await self.broker.send_message(receiver, message)
        except Exception as e:
            logger.error(f"Failed to send message {message} to {receiver}: {e}")
        else:
            logger.debug(f"Sent new message {message} to {receiver}")

    async def handle(self, event: domain_events.NewMessageAdded) -> None:
        async with self.uow:
            message = await self.uow.message_repository.get(event.message_id)

            if message is None:
                raise exceptions.MessageNotFound(event.message_id)

            chat = await self.uow.chat_repository.get(event.chat_id)

            if chat is None:
                raise exceptions.ChatNotFound(event.chat_id)

            message_bytes = orjson.dumps(
                notification_events.NewMessageAdded(
                    event_name="NewMessageAdded",
                    payload=notification_events.MessageAddedPayload(
                        chat_id=message.chat_id,
                        message_id=message.message_id,
                        sender=message.sender,
                        content=message.content,
                        reply_to=message.reply_to,
                        created=message.created,
                    ),
                ).model_dump(mode="json"),
            )
            sent_tasks = [
                self.send_to_receiver(message_bytes, receiver)
                for receiver in chat.participants
            ]

            await asyncio.gather(*sent_tasks)
