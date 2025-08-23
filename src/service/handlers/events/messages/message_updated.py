import asyncio
import logging
import typing

import cqrs
import orjson

from domain import events as domain_events
from infrastructure.brokers import messages_broker
from service import exceptions
from service.interfaces import unit_of_work
from service.requests.ecst_events.messages import message_updated
from service.validators import chats as chat_validators, messages as message_validators

logger = logging.getLogger(__name__)


class MessageUpdatedHandler(cqrs.EventHandler[domain_events.MessageUpdated]):
    """
    Sends message to broker for all receivers.
    """

    def __init__(self, uow: unit_of_work.UoW, broker: messages_broker.MessageBroker):
        self.uow = uow
        self.broker = broker

    async def send_to_receiver(self, message: bytes, receiver: typing.Text) -> None:
        try:
            await self.broker.send_message(receiver, message)
        except Exception as e:
            logger.error(f"Failed to send message updated event to {receiver}: {e}")
        else:
            logger.debug(f"Sent message updated event to {receiver}")

    async def handle(self, event: domain_events.MessageUpdated) -> None:
        async with self.uow:
            chat = await self.uow.chat_repository.get(event.chat_id)
            if chat is None:
                raise exceptions.ChatNotFound(event.chat_id)
            chat_validators.raise_if_sender_not_in_chat(chat, event.chat_id, event.message_sender)

            message = await self.uow.message_repository.get(event.message_id)
            if message is None:
                raise exceptions.MessageNotFound(event.message_id)
            message_validators.raise_if_message_deleted(message)

            message_bytes = orjson.dumps(
                cqrs.NotificationEvent(
                    event_name="MessageUpdated",
                    payload=message_updated.MessageUpdatedPayload(
                        chat_id=message.chat_id,
                        message_id=message.message_id,
                        message_sender=message.sender,
                        message_content=message.content,
                        message_attachments=[attachment for attachment in message.attachments],
                    ),
                ).model_dump(mode="json"),
            )
            sent_tasks = [self.send_to_receiver(message_bytes, receiver.account_id) for receiver in chat.participants]

            await asyncio.gather(*sent_tasks)
