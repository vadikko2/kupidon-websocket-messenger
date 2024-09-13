import typing
import uuid

import cqrs
import pydantic

from domain import attachments, chats, messages
from infrastructure.database.persistent.repositories import (
    attachment_repository,
    chat_repository,
    message_repository,
)

_GLOBAL_CHATS_STORAGE: typing.Dict[uuid.UUID, chats.Chat] = dict()
_GLOBAL_ATTACHMENT_STORAGE: typing.Dict[uuid.UUID, attachments.Attachment] = dict()


class MockMessageRepository(message_repository.MessageRepository):
    def __init__(self):
        self.committed = False
        self._seen_messages = set()

    async def add(self, message: messages.Message) -> None:
        self.committed = False

    async def get(self, message_id: uuid.UUID) -> messages.Message | None:
        for chat in _GLOBAL_CHATS_STORAGE.values():
            for message in chat.history:
                if message.message_id == message_id:
                    self._seen_messages.add(message)
                    return message

    async def update(self, message: messages.Message) -> None:
        self._seen_messages.add(message)
        for i, exist_message in enumerate(
            _GLOBAL_CHATS_STORAGE[message.chat_id].history,
        ):
            if message.message_id == exist_message.message_id:
                _GLOBAL_CHATS_STORAGE[message.chat_id].history[i] = message

        self.committed = False

    async def commit(self):
        self.committed = True

    async def rollback(self):
        pass

    def events(self) -> typing.List[cqrs.DomainEvent]:
        events = []
        for message in self._seen_messages:
            events += message.get_events()
        return events


class MockChatRepository(chat_repository.ChatRepository):
    def __init__(self):
        self.committed = False
        self._seen_chats = set()

    async def add(self, chat: chats.Chat) -> None:
        _GLOBAL_CHATS_STORAGE[chat.chat_id] = chat
        self._seen_chats.add(chat)
        self.committed = False

    async def get(self, chat_id: uuid.UUID) -> chats.Chat | None:
        chat = _GLOBAL_CHATS_STORAGE.get(chat_id)
        if chat:
            self._seen_chats.add(chat)
        return _GLOBAL_CHATS_STORAGE.get(chat_id)

    async def get_chat_history(
        self,
        chat_id: uuid.UUID,
        messages_limit: pydantic.NonNegativeInt,
        latest_message_id: typing.Optional[uuid.UUID] = None,
    ) -> chats.Chat | None:
        latest_message_position = 0

        if latest_message_id is not None:
            for i, message in enumerate(_GLOBAL_CHATS_STORAGE[chat_id].history):
                if message.message_id == latest_message_id:
                    latest_message_position = i
                    break

        if chat_id not in _GLOBAL_CHATS_STORAGE:
            return None

        chat_dict = _GLOBAL_CHATS_STORAGE[chat_id].model_dump(mode="json")
        chat_dict["history"] = chat_dict["history"][
            latest_message_position : latest_message_position + messages_limit
        ]
        new_chat = chats.Chat.model_validate(chat_dict)
        self._seen_chats.add(new_chat)
        return new_chat

    async def get_all(self, participant: typing.Text) -> typing.List[chats.Chat]:
        chats_list: typing.List[chats.Chat] = []
        for chat in _GLOBAL_CHATS_STORAGE.values():
            if participant in chat.participants:
                chats_list.append(chat)
                self._seen_chats.add(chat)
        return chats_list

    async def commit(self):
        self.committed = True

    async def rollback(self):
        pass

    def events(self) -> typing.List[cqrs.DomainEvent]:
        events = []
        for message in self._seen_chats:
            events += message.get_events()
        return events


class MockAttachmentRepository(attachment_repository.AttachmentRepository):
    async def add(self, attachment: attachments.Attachment) -> None:
        _GLOBAL_ATTACHMENT_STORAGE[attachment.attachment_id] = attachment

    async def get(self, attachment_id: uuid.UUID) -> attachments.Attachment | None:
        return _GLOBAL_ATTACHMENT_STORAGE.get(attachment_id)

    async def get_many(
        self,
        *attachment_ids: uuid.UUID,
    ) -> typing.List[attachments.Attachment]:
        return [
            _GLOBAL_ATTACHMENT_STORAGE[attachment_id]
            for attachment_id in attachment_ids
            if attachment_id in _GLOBAL_ATTACHMENT_STORAGE
        ]

    async def get_all(
        self,
        chat_id: uuid.UUID,
        limit: int,
        offset: int,
    ) -> typing.List[attachments.Attachment]:
        attachments_in_chat = [
            attachment
            for attachment in _GLOBAL_ATTACHMENT_STORAGE.values()
            if attachment.chat_id == chat_id
        ]
        return list(
            sorted(
                attachments_in_chat,
                key=lambda attachment: attachment.uploaded,
                reverse=True,
            ),
        )[offset : offset + limit]
