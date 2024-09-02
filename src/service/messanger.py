import typing
import uuid

import orjson

from domain import message as message_entity
from infrastructure.brokers import protocol


class Messanger:
    def __init__(
            self,
            target_account: typing.Text,
            broker: protocol.MessageBroker
    ) -> None:
        self.target_account = target_account
        self.broker = broker

    async def __aenter__(self) -> typing.Self:
        await self.broker.start()
        await self.broker.subscribe(self.target_account)
        return self

    async def __aexit__(self) -> None:
        await self.broker.stop()

    async def send_message(self, message: message_entity.Message) -> None:
        await self.broker.send_message(message.receiver, orjson.dumps(message.model_dump(mode="json")))

    async def get_message(self) -> message_entity.Message | None:
        message = await self.broker.get_message()
        if message is None:
            return None
        return message_entity.Message.model_validate(orjson.loads(message))

    async def mark_as_received(self, message_id: uuid.UUID) -> None:
        pass

    async def mark_as_read(self, message_id: uuid.UUID) -> None:
        pass
