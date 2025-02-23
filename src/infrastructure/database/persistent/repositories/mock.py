import datetime
import typing
import uuid

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
        self._seen = set()

    async def add(self, message: messages.Message) -> None:
        self.committed = False

    async def get(self, message_id: uuid.UUID) -> messages.Message | None:
        for chat in _GLOBAL_CHATS_STORAGE.values():
            for message in chat.history:
                if message.message_id == message_id:
                    self._seen.add(message)
                    return message

    async def update(self, message: messages.Message) -> None:
        self._seen.add(message)
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


class MockChatRepository(chat_repository.ChatRepository):
    def __init__(self):
        self.committed = False
        self._seen = set()

    async def add(self, chat: chats.Chat) -> None:
        _GLOBAL_CHATS_STORAGE[chat.chat_id] = chat
        self._seen.add(chat)
        self.committed = False

    async def get(self, chat_id: uuid.UUID) -> chats.Chat | None:
        chat = _GLOBAL_CHATS_STORAGE.get(chat_id)
        if chat:
            self._seen.add(chat)
        return _GLOBAL_CHATS_STORAGE.get(chat_id)

    async def update(self, chat: chats.Chat) -> None:
        _GLOBAL_CHATS_STORAGE[chat.chat_id] = chat
        self._seen.add(chat)
        self.committed = False

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
        self._seen.add(new_chat)
        return new_chat

    async def get_all(self, participant: typing.Text) -> typing.List[chats.Chat]:
        chats_list: typing.List[chats.Chat] = []
        for chat in _GLOBAL_CHATS_STORAGE.values():
            if participant in chat.participants:
                chats_list.append(chat)
                self._seen.add(chat)
        return chats_list

    async def commit(self):
        self.committed = True

    async def rollback(self):
        pass


class MockAttachmentRepository(attachment_repository.AttachmentRepository):
    def __init__(self):
        self.committed = False
        self._seen = set()

    async def add(self, attachment: attachments.Attachment) -> None:
        _GLOBAL_ATTACHMENT_STORAGE[attachment.attachment_id] = attachment
        self._seen.add(attachment)
        self.committed = False

    async def get(self, attachment_id: uuid.UUID) -> attachments.Attachment | None:
        result = _GLOBAL_ATTACHMENT_STORAGE.get(attachment_id)
        if result:
            self._seen.add(result)
        return result

    async def get_many(
        self,
        *attachment_ids: uuid.UUID,
    ) -> typing.List[attachments.Attachment]:
        result = [
            _GLOBAL_ATTACHMENT_STORAGE[attachment_id]
            for attachment_id in attachment_ids
            if attachment_id in _GLOBAL_ATTACHMENT_STORAGE
        ]
        self._seen.update(result)
        return result

    async def get_all(
        self,
        chat_id: uuid.UUID,
        limit: int,
        offset: int,
    ) -> typing.List[attachments.Attachment]:
        attachments_in_chat = [
            attachment
            for attachment in _GLOBAL_ATTACHMENT_STORAGE.values()
            if attachment.chat_id == chat_id and attachment.uploaded is not None
        ]
        result = list(
            sorted(
                attachments_in_chat,
                key=lambda attachment: attachment.uploaded
                if attachment.uploaded
                else datetime.datetime.min,
                reverse=True,
            ),
        )[offset : offset + limit]

        self._seen.update(result)
        return result

    async def commit(self):
        self.committed = True

    async def rollback(self):
        pass
