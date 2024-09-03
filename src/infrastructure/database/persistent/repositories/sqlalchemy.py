import typing
import uuid

import cqrs

from domain import messages
from infrastructure.database.persistent.repositories import message_repository


class SqlAlchemyMessageRepository(message_repository.MessageRepository):
    def __init__(self):
        self._seen_messages = set()

    async def add(self, message: messages.Message) -> None:
        raise NotImplementedError

    async def get(self, message_id: uuid.UUID) -> messages.Message | None:
        raise NotImplementedError

    async def change_status(
        self,
        message_id: uuid.UUID,
        status: messages.MessageStatus,
    ) -> None:
        raise NotImplementedError

    async def commit(self):
        raise NotImplementedError

    async def rollback(self):
        raise NotImplementedError

    def events(self) -> typing.List[cqrs.DomainEvent]:
        events = []
        for message in self._seen_messages:
            events += message.get_events()
        return events
