import typing
import uuid

import cqrs


class OpenChat(cqrs.Request):
    initiator: typing.Text
    participants: typing.List[typing.Text]
    name: typing.Text | None


class ChatOpened(cqrs.Response):
    chat_id: uuid.UUID
