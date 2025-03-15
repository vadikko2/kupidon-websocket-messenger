import typing
import uuid

import cqrs
import orjson
import pydantic
from redis.asyncio import client

from domain import attachments, chats, messages

CHAT_HISTORY_PREFIX = "chat_history_{}"
CHATS_PREFIX = "chat_{}"
MESSAGES_PREFIX = "message_{}"
PARTICIPANT_CHATS_PREFIX = "participant_chats_{}"
ATTACHMENTS_PREFIX = "attachment_{}"
CHAT_ATTACHMENTS_PREFIX = "chat_attachments_{}"


class MockMessageRepository:
    def __init__(self, redis_pipeline: client.Pipeline):
        self._redis_pipeline = redis_pipeline
        self._seen = set()

    async def add(self, message: messages.Message) -> None:
        await self._redis_pipeline.lpush(  # pyright: ignore[reportGeneralTypeIssues]
            CHAT_HISTORY_PREFIX.format(message.chat_id),
            str(message.message_id),
        )
        await self._redis_pipeline.set(
            MESSAGES_PREFIX.format(message.message_id),
            orjson.dumps(message.model_dump(mode="json")),
        )
        self._seen.add(message)

    async def get(self, message_id: uuid.UUID) -> messages.Message | None:
        message_bytes_coroutine = await self._redis_pipeline.get(
            MESSAGES_PREFIX.format(message_id),
        )
        message_bytes = (await message_bytes_coroutine.execute())[0]
        if not message_bytes:
            return

        message = messages.Message.model_validate(orjson.loads(message_bytes))
        self._seen.add(message)
        return message

    async def update(self, message: messages.Message) -> None:
        await self._redis_pipeline.set(
            MESSAGES_PREFIX.format(message.message_id),
            orjson.dumps(message.model_dump(mode="json")),
        )
        self._seen.add(message)

    def events(self) -> typing.List[cqrs.Event]:
        """
        Returns new domain ecst_events
        """
        new_events = []
        for message in self._seen:
            while message.event_list:
                new_events.append(message.event_list.pop())
        return new_events


class MockChatRepository:
    def __init__(self, redis_pipeline: client.Pipeline):
        self._redis_pipeline = redis_pipeline
        self._seen = set()

    async def add(self, chat: chats.Chat) -> None:
        for participant in chat.participants:
            await self._redis_pipeline.lpush(  # pyright: ignore[reportGeneralTypeIssues]
                PARTICIPANT_CHATS_PREFIX.format(participant),
                str(chat.chat_id),
            )
        await self._redis_pipeline.set(
            CHATS_PREFIX.format(chat.chat_id),
            orjson.dumps(chat.model_dump(mode="json")),
        )
        self._seen.add(chat)

    async def get(self, chat_id: uuid.UUID) -> chats.Chat | None:
        chat_bytes_coroutine = await self._redis_pipeline.get(
            CHATS_PREFIX.format(chat_id),
        )
        chat_bytes = (await chat_bytes_coroutine.execute())[0]

        if not chat_bytes:
            return

        chat = chats.Chat.model_validate(orjson.loads(chat_bytes))
        self._seen.add(chat)
        return chat

    async def update(self, chat: chats.Chat) -> None:
        await self._redis_pipeline.set(
            CHATS_PREFIX.format(chat.chat_id),
            orjson.dumps(chat.model_dump(mode="json")),
        )
        self._seen.add(chat)

    async def get_chat_history(
        self,
        chat_id: uuid.UUID,
        messages_limit: pydantic.NonNegativeInt,
        latest_message_id: typing.Optional[uuid.UUID] = None,
        reverse: bool = False,
    ) -> chats.Chat | None:
        chat_bytes_coroutine = await self._redis_pipeline.get(
            CHATS_PREFIX.format(chat_id),
        )
        chat_bytes = (await chat_bytes_coroutine.execute())[0]

        if not chat_bytes:
            return
        chat = chats.Chat.model_validate(orjson.loads(chat_bytes))

        all_chat_messages_bytes_coroutine = await self._redis_pipeline.lrange(
            # pyright: ignore[reportGeneralTypeIssues]
            CHAT_HISTORY_PREFIX.format(chat_id),
            0,
            -1,
        )

        all_chat_messages_bytes = (await all_chat_messages_bytes_coroutine.execute())[0]  # pyright: ignore[reportAttributeAccessIssue]
        if not all_chat_messages_bytes:
            self._seen.add(chat)
            return chat

        messages_in_chat = [
            uuid.UUID(message_bytes) for message_bytes in all_chat_messages_bytes
        ]

        messages_list_bytes_coroutine = self._redis_pipeline.mget(
            *[MESSAGES_PREFIX.format(message_id) for message_id in messages_in_chat],
        )

        messages_list_bytes = (await messages_list_bytes_coroutine.execute())[0]  # pyright: ignore[reportAttributeAccessIssue]

        sorted_messages = sorted(
            [
                messages.Message.model_validate(orjson.loads(mb))
                for mb in messages_list_bytes
            ],
            key=lambda msg: msg.created,
            reverse=not reverse,
        )

        add_to_history = latest_message_id is None

        for msg in sorted_messages:
            if msg.message_id == latest_message_id:
                add_to_history = True
            if add_to_history:
                chat.history.append(msg)
                if len(chat.history) == messages_limit:
                    break
        return chat

    async def get_all(self, participant: typing.Text) -> typing.List[chats.Chat]:
        participant_chats_bytes_coroutine = await self._redis_pipeline.lrange(
            # pyright: ignore[reportGeneralTypeIssues]
            PARTICIPANT_CHATS_PREFIX.format(participant),
            0,
            -1,
        )
        participant_chats_bytes = (await participant_chats_bytes_coroutine.execute())[0]  # pyright: ignore[reportAttributeAccessIssue]
        if not participant_chats_bytes:
            return []

        chat_ides = [
            uuid.UUID(chat_id_bytes) for chat_id_bytes in participant_chats_bytes
        ]
        chats_bytes_coroutine = await self._redis_pipeline.mget(
            *[CHATS_PREFIX.format(chat_id) for chat_id in chat_ides],
        )
        chats_bytes = (await chats_bytes_coroutine.execute())[0]
        if not chats_bytes:
            return []

        result = sorted(
            [
                chats.Chat.model_validate(orjson.loads(chat_bytes))
                for chat_bytes in chats_bytes
                if chat_bytes
            ],
            key=lambda chat: chat.last_activity_timestamp,
            reverse=True,
        )
        self._seen.update(result)
        return result

    def events(self):
        new_events = []
        for attachment in self._seen:
            while attachment.event_list:
                new_events.append(attachment.event_list.pop())
        return new_events


class MockAttachmentRepository:
    def __init__(self, redis_pipeline: client.Pipeline):
        self._redis_pipeline = redis_pipeline
        self._seen = set()

    async def add(self, attachment: attachments.Attachment) -> None:
        await self._redis_pipeline.set(
            ATTACHMENTS_PREFIX.format(attachment.attachment_id),
            orjson.dumps(attachment.model_dump(mode="json")),
        )
        await self._redis_pipeline.lpush(  # pyright: ignore[reportGeneralTypeIssues]
            CHAT_ATTACHMENTS_PREFIX.format(attachment.chat_id),
            str(attachment.attachment_id),
        )
        self._seen.add(attachment)

    async def get(self, attachment_id: uuid.UUID) -> attachments.Attachment | None:
        attachment_bytes_coroutine = await self._redis_pipeline.get(
            ATTACHMENTS_PREFIX.format(attachment_id),
        )
        attachment_bytes = (await attachment_bytes_coroutine.execute())[0]
        if not attachment_bytes:
            return

        attachment = attachments.Attachment.model_validate(
            orjson.loads(attachment_bytes),
        )
        self._seen.add(attachment)
        return attachment

    async def get_many(
        self,
        *attachment_ids: uuid.UUID,
    ) -> typing.List[attachments.Attachment]:
        if not attachment_ids:
            return []

        attachments_bytes_coroutine = await self._redis_pipeline.mget(
            *[
                ATTACHMENTS_PREFIX.format(attachment_id)
                for attachment_id in attachment_ids
            ],
        )
        attachments_bytes = (await attachments_bytes_coroutine.execute())[0]
        if not attachments_bytes:
            return []

        result = [
            attachments.Attachment.model_validate(orjson.loads(attachment_bytes))
            for attachment_bytes in attachments_bytes
            if attachment_bytes
        ]
        self._seen.update(result)
        return result

    async def get_all(
        self,
        chat_id: uuid.UUID,
        limit: int,
        offset: int,
    ) -> typing.List[attachments.Attachment]:
        attachments_in_chat_bytes_coroutine = await self._redis_pipeline.lrange(
            # pyright: ignore[reportGeneralTypeIssues]
            CHAT_ATTACHMENTS_PREFIX.format(chat_id),
            0,
            -1,
        )
        attachments_in_chat_bytes = (
            await attachments_in_chat_bytes_coroutine.execute()  # pyright: ignore[reportAttributeAccessIssue]
        )[0]  # pyright: ignore[reportAttributeAccessIssue]
        if not attachments_in_chat_bytes:
            return []

        attachments_bytes_coroutine = await self._redis_pipeline.mget(
            *[
                ATTACHMENTS_PREFIX.format(attachment_id)
                for attachment_id in attachments_in_chat_bytes
            ],
        )
        attachments_bytes = (await attachments_bytes_coroutine.execute())[0]
        if not attachments_bytes:
            return []

        result = sorted(
            [
                attachments.Attachment.model_validate(orjson.loads(attachment_bytes))
                for attachment_bytes in attachments_bytes
                if attachment_bytes
            ],
            key=lambda attachment: attachment.created,
            reverse=True,
        )
        self._seen.update(result[offset : offset + limit])
        return result[offset : offset + limit]

    def events(self) -> typing.List[cqrs.Event]:
        new_events = []
        for attachment in self._seen:
            while attachment.event_list:
                new_events.append(attachment.event_list.pop())
        return new_events
