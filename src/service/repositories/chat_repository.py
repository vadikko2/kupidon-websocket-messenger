import typing
import uuid

import cqrs
import pydantic

from domain import chats


class ChatRepository(typing.Protocol):
    _seen: typing.Set[chats.Chat]

    async def add(self, chat: chats.Chat) -> None:
        """
        Adds new chat
        """
        raise NotImplementedError

    async def get(self, chat_id: uuid.UUID) -> chats.Chat | None:
        """
        Gets specified chat
        """
        raise NotImplementedError

    async def update(self, chat: chats.Chat) -> None:
        """
        Updates chat
        """
        raise NotImplementedError

    async def get_chat_history(
        self,
        chat_id: uuid.UUID,
        messages_limit: pydantic.NonNegativeInt,
        latest_message_id: typing.Optional[uuid.UUID] = None,
        reverse: bool = False,
    ) -> chats.Chat | None:
        """
        Returns chat history
        """
        raise NotImplementedError

    async def get_all(self, participant: typing.Text) -> typing.List[chats.Chat]:
        """
        Gets all chats
        """
        raise NotImplementedError

    def events(self) -> typing.List[cqrs.Event]:
        """
        Returns new domain ecst_events
        """
        raise NotImplementedError
