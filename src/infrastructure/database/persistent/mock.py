import collections
import typing
import uuid

from domain import message as message_entity
from infrastructure.database.persistent import protocol
from infrastructure.database.persistent.protocol import MessageRepository


class MockMessageRepository(protocol.MessageRepository):

    def __init__(self, storage: typing.DefaultDict[typing.Text, typing.List[message_entity.Message]]):
        self.storage = storage
        self.committed = False

    async def get_new_messages(self, receiver: typing.Text) -> typing.List[message_entity.Message]:
        return self.storage[receiver]

    async def add(self, message: message_entity.Message) -> None:
        self.storage[message.receiver].append(message)
        self.committed = False

    async def get(self, message_id: uuid.UUID) -> message_entity.Message | None:
        for messages in self.storage.values():
            for message in messages:
                if message.message_id == message_id:
                    return message

    async def change_status(self, message_id: uuid.UUID, status: message_entity.MessageStatus) -> None:
        message = await self.get(message_id)
        for messages in self.storage.values():
            for message in messages:
                if message.message_id == message_id:
                    message.status = status
        self.committed = False

    async def commit(self):
        self.committed = True

    async def rollback(self):
        pass


_GLOBAL_STORAGE = collections.defaultdict(list)


class MockMessageUoW(protocol.MessageUoW):

    async def __aenter__(self) -> MessageRepository:
        self.repository = MockMessageRepository(_GLOBAL_STORAGE)
        return self.repository
