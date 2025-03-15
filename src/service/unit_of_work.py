import abc
import typing

import cqrs
import redis.asyncio as redis

from infrastructure.database.persistent import mock
from service.repositories import (
    attachment_repository,
    chat_repository,
    message_repository,
)


class UoW(abc.ABC):
    chat_repository: chat_repository.ChatRepository
    message_repository: message_repository.MessageRepository
    attachment_repository: attachment_repository.AttachmentRepository

    @abc.abstractmethod
    async def __aenter__(self) -> typing.Self:
        raise NotImplementedError

    async def commit(self):
        raise NotImplementedError

    async def rollback(self):
        raise NotImplementedError

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.rollback()

    def get_events(self) -> typing.List[cqrs.Event]:
        return (
            self.message_repository.events()
            + self.chat_repository.events()
            + self.attachment_repository.events()
        )


class MockMessageUoW(UoW):
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
        return self

    async def commit(self):
        await self._redis_pipeline.execute()

    async def rollback(self):
        try:
            await self._redis_pipeline.discard()
        finally:
            del self._redis_pipeline
