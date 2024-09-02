import collections
import typing
import uuid

from domain import message as message_entity
from infrastructure.database.persistent import protocol
from infrastructure.database.persistent.protocol import MessageRepository

_InMemoryStorage: typing.TypeAlias = typing.DefaultDict[
    typing.Text,
    typing.DefaultDict[typing.Text, typing.List[message_entity.Message]],
]


class MockMessageRepository(protocol.MessageRepository):
    def __init__(self, storage: _InMemoryStorage):
        self.storage = storage
        self.committed = False

    async def get_new_messages(
        self,
        receiver: typing.Text,
    ) -> typing.List[message_entity.Message]:
        new_messages = []
        for partner in self.storage[receiver]:
            for message in self.storage[receiver][partner]:
                if message.status == message_entity.MessageStatus.SENT:
                    new_messages.append(message)
        return new_messages

    async def get_history(
        self,
        account: typing.Text,
        partner: typing.Text,
        limit: int,
        latest_id: uuid.UUID | None = None,
    ) -> typing.List[message_entity.Message]:
        received_messages = sorted(
            self.storage[partner][account],
            key=lambda m: m.created,
            reverse=True,
        )
        send_messages = sorted(
            self.storage[account][partner],
            key=lambda m: m.created,
            reverse=True,
        )

        all_messages = received_messages + send_messages

        latest_position = 0
        if latest_id is not None:
            latest_position = next(
                (i for i, m in enumerate(all_messages) if m.message_id == latest_id),
                0,
            )

        return all_messages[latest_position : latest_position + limit]

    async def add(self, message: message_entity.Message) -> None:
        self.storage[message.receiver][message.sender].append(message)
        self.committed = False

    async def get(self, message_id: uuid.UUID) -> message_entity.Message | None:
        for receivers in self.storage.values():
            for messages in receivers.values():
                for message in messages:
                    if message.message_id == message_id:
                        return message

    async def change_status(
        self,
        message_id: uuid.UUID,
        status: message_entity.MessageStatus,
    ) -> None:
        for receivers in self.storage.values():
            for messages in receivers.values():
                for message in messages:
                    if message.message_id == message_id:
                        message.status = status
        self.committed = False

    async def commit(self):
        self.committed = True

    async def rollback(self):
        pass


_GLOBAL_STORAGE = collections.defaultdict(lambda: collections.defaultdict(list))


class MockMessageUoW(protocol.MessageUoW):
    async def __aenter__(self) -> MessageRepository:
        self.repository = MockMessageRepository(_GLOBAL_STORAGE)
        return self.repository
