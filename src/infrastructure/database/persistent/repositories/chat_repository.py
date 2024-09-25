import abc
import typing
import uuid

import cqrs
import pydantic

from domain import chats


class ChatRepository(abc.ABC):
    _seen: typing.Set[chats.Chat]

    @abc.abstractmethod
    async def add(self, chat: chats.Chat) -> None:
        """
        Adds new chat
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, chat_id: uuid.UUID) -> chats.Chat | None:
        """
        Gets specified chat
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_chat_history(
        self,
        chat_id: uuid.UUID,
        messages_limit: pydantic.NonNegativeInt,
        latest_message_id: typing.Optional[uuid.UUID] = None,
    ) -> chats.Chat | None:
        """
        Returns chat history
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_all(self, participant: typing.Text) -> typing.List[chats.Chat]:
        """
        Gets all chats
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
        Returns new domain ecst_events
        """
        new_events = []
        for attachment in self._seen:
            while attachment.event_list:
                new_events.append(attachment.event_list.pop())
        return new_events
