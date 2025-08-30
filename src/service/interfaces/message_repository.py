import typing
import uuid

import cqrs

from domain import attachments, messages


class MessageRepository(typing.Protocol):
    _seen: set[messages.Message | attachments.Attachment]

    async def add(self, message: messages.Message) -> None:
        """
        Adds new message
        """
        raise NotImplementedError

    async def get(self, message_id: uuid.UUID) -> messages.Message | None:
        """
        Gets specified message
        """
        raise NotImplementedError

    async def update(self, message: messages.Message) -> None:
        """
        Changes message status
        """
        raise NotImplementedError

    def events(self) -> list[cqrs.Event]:
        """
        Returns new domain events
        """
        raise NotImplementedError


class ReadMessageRepository(typing.Protocol):
    _seen: set[messages.ReedMessage]

    async def last_read(
        self,
        account_id: str,
        chat_id: uuid.UUID,
    ) -> messages.ReedMessage | None:
        """
        Returns last read message by account in specified chat
        """
        raise NotImplementedError

    async def last_read_many(
        self,
        account_id: str,
        chat_ids: list[uuid.UUID],
    ) -> list[messages.ReedMessage | None]:
        """
        Returns last read messages by account in specified chats
        """
        raise NotImplementedError

    async def register(self, message: messages.ReedMessage) -> None:
        """
        Registers message as seen by
        """
        raise NotImplementedError
