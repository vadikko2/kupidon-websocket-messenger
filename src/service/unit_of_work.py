import abc
import typing

import cqrs

from infrastructure.database.persistent.repositories import (
    attachment_repository,
    chat_repository,
    message_repository,
    mock,
)


class UoW(abc.ABC):
    chat_repository: chat_repository.ChatRepository
    message_repository: message_repository.MessageRepository
    attachment_repository: attachment_repository.AttachmentRepository

    @abc.abstractmethod
    async def __aenter__(self) -> typing.Self:
        raise NotImplementedError

    async def commit(self):
        await self.message_repository.commit()
        await self.chat_repository.commit()
        await self.attachment_repository.commit()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.message_repository.rollback()
        await self.chat_repository.rollback()
        await self.attachment_repository.rollback()

    def get_events(self) -> typing.List[cqrs.DomainEvent]:
        return (
            self.message_repository.events()
            + self.chat_repository.events()
            + self.attachment_repository.events()
        )


class MockMessageUoW(UoW):
    async def __aenter__(self):
        self.message_repository = mock.MockMessageRepository()
        self.chat_repository = mock.MockChatRepository()
        self.attachment_repository = mock.MockAttachmentRepository()
        return self
