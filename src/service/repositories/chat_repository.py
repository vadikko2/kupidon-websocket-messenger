import typing
import uuid

import cqrs

from domain import chats, messages


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
        messages_limit: int | None = None,
        latest_message_id: typing.Optional[uuid.UUID] = None,
        reverse: bool = False,
    ) -> chats.Chat | None:
        """
        Returns chat history
        """
        raise NotImplementedError

    async def get_next_message_id(
        self,
        chat_id: uuid.UUID,
        target_message_id: uuid.UUID,
    ) -> messages.Message | None:
        """
        Returns next message
        """
        raise NotImplementedError

    async def get_previous_message_id(
        self,
        chat_id: uuid.UUID,
        target_message_id: uuid.UUID,
    ) -> messages.Message | None:
        """
        Returns previous message
        """
        raise NotImplementedError

    async def count_after(
        self,
        chat_id: uuid.UUID,
        message_id: uuid.UUID | None,
    ) -> int:
        """
        Returns count of messages after specified message
        """
        raise NotImplementedError

    async def count_after_many(
        self,
        *message: typing.Tuple[uuid.UUID, uuid.UUID | None],
    ) -> typing.List[int]:
        """
        Returns count of messages after specified messages
        """
        raise NotImplementedError

    async def get_all(self, participant: typing.Text) -> typing.List[chats.Chat]:
        """
        Gets all chats
        """
        raise NotImplementedError

    def events(self) -> typing.List[cqrs.Event]:
        """
        Returns new domain events
        """
        raise NotImplementedError
