import typing
import uuid

import cqrs
import orjson
from redis.asyncio import client

from domain import attachments, chats, messages

CHAT_HISTORY_PREFIX = "chat_history_{}"
CHATS_PREFIX = "chat_{}"
MESSAGES_PREFIX = "message_{}"
PARTICIPANT_CHATS_PREFIX = "participant_chats_{}"
ATTACHMENTS_PREFIX = "attachment_{}"
CHAT_ATTACHMENTS_PREFIX = "chat_attachments_{}"
READ_MESSAGES_PREFIX = "read_messages_{chat_id}_{participant_id}"


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
                PARTICIPANT_CHATS_PREFIX.format(participant.account_id),
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
        messages_limit: int | None = None,
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

        messages_in_chat = [uuid.UUID(message_bytes) for message_bytes in all_chat_messages_bytes]

        messages_list_bytes_coroutine = self._redis_pipeline.mget(
            *[MESSAGES_PREFIX.format(message_id) for message_id in messages_in_chat],
        )

        messages_list_bytes = (await messages_list_bytes_coroutine.execute())[0]  # pyright: ignore[reportAttributeAccessIssue]

        sorted_messages = sorted(
            [messages.Message.model_validate(orjson.loads(mb)) for mb in messages_list_bytes],
            key=lambda msg: msg.created,
            reverse=not reverse,
        )

        add_to_history = latest_message_id is None

        for msg in sorted_messages:
            if msg.message_id == latest_message_id:
                add_to_history = True
            if add_to_history:
                chat.history.append(msg)
                if messages_limit and len(chat.history) == messages_limit:
                    break
        return chat

    async def get_all_messages_in_chat(self, chat_id: uuid.UUID) -> typing.List[messages.Message]:
        all_chat_messages_bytes_coroutine = await self._redis_pipeline.lrange(
            # pyright: ignore[reportGeneralTypeIssues]
            CHAT_HISTORY_PREFIX.format(chat_id),
            0,
            -1,
        )

        all_chat_messages_bytes = (await all_chat_messages_bytes_coroutine.execute())[0]  # pyright: ignore[reportAttributeAccessIssue]

        all_messages = []
        for message in all_chat_messages_bytes:
            message_id = uuid.UUID(message)
            message_bytes_coroutine = await self._redis_pipeline.get(
                MESSAGES_PREFIX.format(message_id),
            )
            message_bytes = (await message_bytes_coroutine.execute())[0]
            if not message_bytes:
                continue

            all_messages.append(messages.Message.model_validate(orjson.loads(message_bytes)))

        return all_messages

    async def get_next_message_id(
        self,
        chat_id: uuid.UUID,
        target_message_id: uuid.UUID,
    ) -> messages.Message | None:
        all_messages = sorted(await self.get_all_messages_in_chat(chat_id), key=lambda msg: msg.created)

        for position, message in enumerate(all_messages):
            if message.message_id == target_message_id:
                if position < len(all_messages) - 1:
                    return all_messages[position + 1]
                return

        return

    async def get_previous_message_id(
        self,
        chat_id: uuid.UUID,
        target_message_id: uuid.UUID,
    ) -> messages.Message | None:
        all_messages = sorted(await self.get_all_messages_in_chat(chat_id), key=lambda msg: msg.created)

        for position, message in enumerate(all_messages):
            if message.message_id == target_message_id:
                if position > 0:
                    return all_messages[position - 1]
                return
        return

    async def count_after(
        self,
        chat_id: uuid.UUID,
        message_id: uuid.UUID | None,
    ) -> int:
        history = await self.get_chat_history(
            chat_id,
            latest_message_id=message_id,
            reverse=True,
        )
        return max(0, len(history.history) - 1) if history else 0

    async def count_after_many(
        self,
        *message: typing.Tuple[uuid.UUID, uuid.UUID | None],
    ) -> typing.List[int]:
        """
        Returns count of messages after specified messages
        """
        result = []
        for chat_id, msg_id in message:
            result.append(await self.count_after(chat_id, msg_id))
        return result

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

        chat_ides = [uuid.UUID(chat_id_bytes) for chat_id_bytes in participant_chats_bytes]
        chats_bytes_coroutine = await self._redis_pipeline.mget(
            *[CHATS_PREFIX.format(chat_id) for chat_id in chat_ides],
        )
        chats_bytes = (await chats_bytes_coroutine.execute())[0]
        if not chats_bytes:
            return []

        result = sorted(
            [chats.Chat.model_validate(orjson.loads(chat_bytes)) for chat_bytes in chats_bytes if chat_bytes],
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
            *[ATTACHMENTS_PREFIX.format(attachment_id) for attachment_id in attachment_ids],
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
        attachments_in_chat_bytes = (await attachments_in_chat_bytes_coroutine.execute())[0]  # pyright: ignore[reportAttributeAccessIssue]
        if not attachments_in_chat_bytes:
            return []

        attachments_bytes_coroutine = await self._redis_pipeline.mget(
            *[ATTACHMENTS_PREFIX.format(attachment_id) for attachment_id in attachments_in_chat_bytes],
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


class MockReadMessageRepository:
    def __init__(self, redis_pipeline: client.Pipeline):
        self._redis_pipeline = redis_pipeline
        self._seen = set()

    async def last_read(
        self,
        account_id: typing.Text,
        chat_id: uuid.UUID,
    ) -> messages.ReedMessage | None:
        seen_messages_bytes_coroutine = await self._redis_pipeline.lrange(  # pyright: ignore[reportGeneralTypeIssues]
            READ_MESSAGES_PREFIX.format(
                chat_id=chat_id,
                participant_id=account_id,
            ),
            0,
            -1,
        )
        if not seen_messages_bytes_coroutine:
            return None

        seen_messages_bytes = (await seen_messages_bytes_coroutine.execute())[0]  # pyright: ignore[reportAttributeAccessIssue]
        if not seen_messages_bytes:
            return None

        seen_message = map(
            lambda x: messages.ReedMessage.model_validate(orjson.loads(x)),
            seen_messages_bytes,
        )
        last_message = max(seen_message, key=lambda x: x.timestamp)
        self._seen.add(last_message)
        return last_message

    async def last_read_many(
        self,
        account_id: typing.Text,
        chat_ids: typing.List[uuid.UUID],
    ) -> typing.List[messages.ReedMessage | None]:
        result = []
        for chat_id in chat_ids:
            result.append(await self.last_read(account_id, chat_id))

        return result

    async def register(self, message: messages.ReedMessage) -> None:
        await self._redis_pipeline.lpush(  # pyright: ignore[reportGeneralTypeIssues]
            READ_MESSAGES_PREFIX.format(
                chat_id=message.message.chat_id,
                participant_id=message.actor,
            ),
            orjson.dumps(message.model_dump(mode="json")),
        )
