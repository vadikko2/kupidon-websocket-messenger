import abc
import typing

import cqrs

from service.interfaces import (
    attachment_repository,
    chat_repository,
    message_repository as msg_repository,
)


class UoW(abc.ABC):
    chat_repository: chat_repository.ChatRepository
    message_repository: msg_repository.MessageRepository
    read_message_repository: msg_repository.ReadMessageRepository
    attachment_repository: attachment_repository.AttachmentRepository

    @abc.abstractmethod
    async def __aenter__(self) -> typing.Self:
        raise NotImplementedError

    @abc.abstractmethod
    async def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def rollback(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    @abc.abstractmethod
    def get_events(self) -> typing.Iterable[cqrs.Event]:
        raise NotImplementedError
