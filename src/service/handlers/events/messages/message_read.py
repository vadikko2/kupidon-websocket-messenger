import logging

import cqrs
import orjson

from domain import events
from infrastructure.brokers import messages_broker
from service import exceptions
from service.interfaces import unit_of_work
from service.requests.ecst_events.messages import message_read
from service.validators import chats as chat_validators, messages as message_validators

logger = logging.getLogger(__name__)


class MessageReadHandler(cqrs.EventHandler[events.MessageRead]):
    def __init__(self, uow: unit_of_work.UoW, broker: messages_broker.MessageBroker):
        self.uow = uow
        self.broker = broker

    async def handle(self, event: events.MessageRead) -> None:
        async with self.uow:
            chat = await self.uow.chat_repository.get(event.chat_id)
            if chat is None:
                raise exceptions.ChatNotFound(event.chat_id)
            chat_validators.raise_if_sender_not_in_chat(chat, event.chat_id, event.reader_id)

            message = await self.uow.message_repository.get(event.message_id)
            if message is None:
                raise exceptions.MessageNotFound(event.message_id)
            message_validators.raise_if_message_deleted(message)

            await self.broker.send_message(
                message.sender,
                orjson.dumps(
                    cqrs.NotificationEvent(
                        event_name="MessageReed",
                        payload=message_read.MessageReadPayload(
                            chat_id=message.chat_id,
                            message_id=message.message_id,
                            reader=event.reader_id,
                        ),
                    ).model_dump(mode="json"),
                ),
            )
