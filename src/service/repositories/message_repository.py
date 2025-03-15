import typing
import uuid

import cqrs

from domain import messages


class MessageRepository(typing.Protocol):
    _seen: typing.Set[messages.Message]

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

    def events(self) -> typing.List[cqrs.Event]:
        """
        Returns new domain ecst_events
        """
        raise NotImplementedError
