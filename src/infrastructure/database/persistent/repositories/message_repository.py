import abc
import typing
import uuid

import cqrs

from domain import messages


class MessageRepository(abc.ABC):
    _seen: typing.Set[messages.Message]

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

    def events(self) -> typing.List[cqrs.DomainEvent]:
        """
        Returns new domain events
        """
        new_events = []
        for message in self._seen:
            while message.event_list:
                new_events.append(message.event_list.pop())
        return new_events
