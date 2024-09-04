import logging

import cqrs
import orjson

from domain import events
from infrastructure.brokers import protocol as broker_protocol
from service import exceptions, unit_of_work

logger = logging.getLogger(__name__)


class NewMessageAddedHandler(cqrs.EventHandler[events.NewMessageAdded]):
    """
    Sends message to broker for all receivers.
    """

    def __init__(self, uow: unit_of_work.UoW, broker: broker_protocol.MessageBroker):
        self.uow = uow
        self.broker = broker

    async def handle(self, event: events.NewMessageAdded) -> None:
        async with self.uow:
            message = await self.uow.message_repository.get(event.message_id)

            if message is None:
                raise exceptions.MessageNotFound(event.message_id)

            chat = await self.uow.chat_repository.get(event.chat_id)

            if chat is None:
                raise exceptions.ChatNotFound(event.chat_id)

            for receiver in chat.participants:
                try:
                    logger.debug(
                        f"Sending new message {message.message_id} to {receiver}",
                    )
                    await self.broker.send_message(
                        receiver,
                        orjson.dumps(message.model_dump(mode="json")),
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to send message {message.message_id} to {receiver}: {e}",
                    )
