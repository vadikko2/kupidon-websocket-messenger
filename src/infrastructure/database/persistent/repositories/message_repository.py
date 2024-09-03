import abc
import typing
import uuid

import cqrs

from domain import messages


class MessageRepository(abc.ABC):
    _seen_messages: typing.Set[messages.Message]

    @abc.abstractmethod
    async def add(self, message: messages.Message) -> None:
        """
        Adds new message
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, message_id: uuid.UUID) -> messages.Message | None:
        """
        Gets specified message
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, message: messages.Message) -> None:
        """
        Changes message status
        """
        raise NotImplementedError

    @abc.abstractmethod
    def events(self) -> typing.List[cqrs.DomainEvent]:
        """
        Returns domain events
        """
        events = []
        for message in self._seen_messages:
            events += message.get_events()

        return events

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
