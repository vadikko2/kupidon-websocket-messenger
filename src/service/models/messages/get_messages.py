import datetime
import typing

import cqrs
import pydantic

from service.models.attachments import get_attachments


class GetMessages(cqrs.Request):
    chat_id: pydantic.UUID4
    account: str
    messages_limit: pydantic.NonNegativeInt
    latest_message_id: pydantic.UUID4 | None = None
    reverse: bool = False


class ReactionsUnderMessage(cqrs.Request):
    message_id: pydantic.UUID4
    emoji: str
    count: pydantic.PositiveInt


class MessageInfo(cqrs.Request):
    chat_id: pydantic.UUID4
    message_id: pydantic.UUID4
    sender: str
    content: str | None
    attachments: list[get_attachments.AttachmentInfo]
    reactions: list[ReactionsUnderMessage]
    reply_to: typing.Optional["MessagePreview"]
    read: bool
    created: datetime.datetime
    updated: datetime.datetime


class Messages(cqrs.Response):
    messages: list[MessageInfo] = pydantic.Field(default_factory=list)
    next_message_id: pydantic.UUID4 | None
    prev_message_id: pydantic.UUID4 | None


class GetMessagePreview(cqrs.Request):
    message_id: pydantic.UUID4
    account: str


class MessagePreview(cqrs.Response):
    chat_id: pydantic.UUID4
    message_id: pydantic.UUID4
    sender: str
    content: str | None
    created: datetime.datetime
