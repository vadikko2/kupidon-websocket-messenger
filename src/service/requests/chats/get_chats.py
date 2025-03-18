import datetime
import typing
import uuid

import cqrs
import pydantic


class GetChats(cqrs.Request):
    participant: typing.Text


class ChatInfo(cqrs.Response):
    chat_id: uuid.UUID
    name: typing.Text
    avatar: pydantic.AnyHttpUrl | None = None
    participants_count: pydantic.NonNegativeInt
    last_activity_timestamp: typing.Optional[datetime.datetime]
    last_message_id: uuid.UUID | None = None
    last_read_message_id: uuid.UUID | None = None
    not_read_messages_count: pydantic.NonNegativeInt = pydantic.Field(
        description="Count of not read messages",
        default=0,
    )


class Chats(cqrs.Response):
    chats: typing.Sequence[ChatInfo]
