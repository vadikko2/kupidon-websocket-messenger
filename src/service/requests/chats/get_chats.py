import datetime
import typing
import uuid

import cqrs


class GetChats(cqrs.Request):
    participant: typing.Text


class ChatInfo(cqrs.Response):
    chat_id: uuid.UUID
    name: typing.Text | None
    last_activity_timestamp: typing.Optional[datetime.datetime]
    last_message_id: uuid.UUID | None


class Chats(cqrs.Response):
    chats: typing.Sequence[ChatInfo]
