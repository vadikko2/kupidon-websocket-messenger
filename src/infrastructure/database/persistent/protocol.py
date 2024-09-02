import abc
import typing
import uuid

from domain import message as message_entity


class MessageRepository(abc.ABC):
    @abc.abstractmethod
    async def get_new_messages(self, receiver: typing.Text) -> typing.List[message_entity.Message]:
        """
        Returns new messages for the specified account
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def add(self, message: message_entity.Message) -> None:
        """
        Adds new message
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, message_id: uuid.UUID) -> message_entity.Message | None:
        """
        Gets specified message
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def change_status(self, message_id: uuid.UUID, status: message_entity.MessageStatus) -> None:
        """
        Changes message status
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def commit(self):
        """
        Commits changes
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def rollback(self):
        """
        Rollbacks changes
        """
        raise NotImplementedError


class MessageUoW(abc.ABC):
    repository: MessageRepository

    @abc.abstractmethod
    async def __aenter__(self) -> MessageRepository:
        raise NotImplementedError

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.repository.rollback()
