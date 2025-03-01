import typing
import uuid

import cqrs
import pydantic


class OpenChat(cqrs.Request):
    initiator: typing.Text
    participants: typing.List[typing.Text]
    name: typing.Text
    avatar: pydantic.AnyHttpUrl | None = pydantic.Field(default=None)


class ChatOpened(cqrs.Response):
    chat_id: uuid.UUID
