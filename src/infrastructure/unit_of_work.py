import itertools
import typing

import cqrs
import redis.asyncio as redis

from infrastructure.database.persistent import mock
from service.interfaces import unit_of_work


class MockMessageUoW(unit_of_work.UoW):
    def __init__(self, redis_factory: typing.Callable[[], redis.Redis]):
        self._redis_factory = redis_factory

    async def __aenter__(self):
        self._redis_pipeline = self._redis_factory().pipeline(transaction=True)
        self.message_repository = mock.MockMessageRepository(
            redis_pipeline=self._redis_pipeline,
        )
        self.chat_repository = mock.MockChatRepository(
            redis_pipeline=self._redis_pipeline,
        )
        self.attachment_repository = mock.MockAttachmentRepository(
            redis_pipeline=self._redis_pipeline,
        )
        self.read_message_repository = mock.MockReadMessageRepository(
            redis_pipeline=self._redis_pipeline,
        )
        return self

    async def commit(self):
        await self._redis_pipeline.execute()

    async def rollback(self):
        try:
            await self._redis_pipeline.discard()
        finally:
            del self._redis_pipeline

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.rollback()

    def get_events(self) -> typing.Iterable[cqrs.Event]:
        return itertools.chain(
            self.message_repository.events(),
            self.chat_repository.events(),
            self.attachment_repository.events(),
        )
