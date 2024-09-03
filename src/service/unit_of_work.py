import abc
import typing

from infrastructure.database.persistent.repositories import (
    chat_repository,
    message_repository,
    mock,
)


class UoW(abc.ABC):
    message_repository: message_repository.MessageRepository
    chat_repository: chat_repository.ChatRepository

    @abc.abstractmethod
    async def __aenter__(self) -> typing.Self:
        raise NotImplementedError

    async def commit(self):
        await self.message_repository.commit()
        await self.chat_repository.commit()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.message_repository.rollback()
        await self.chat_repository.rollback()

    def get_events(self):
        return self.message_repository.events() + self.chat_repository.events()


class MockMessageUoW(UoW):
    async def __aenter__(self):
        self.message_repository = mock.MockMessageRepository()
        self.chat_repository = mock.MockChatRepository()

        return self
