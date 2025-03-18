import datetime
import typing
import uuid

import cqrs
import pydantic

from service.requests.attachments import get_attachments


class GetMessages(cqrs.Request):
    chat_id: uuid.UUID
    account: typing.Text
    messages_limit: pydantic.NonNegativeInt
    latest_message_id: typing.Optional[uuid.UUID] = None
    reverse: pydantic.StrictBool = False


class ReactionsUnderMessage(cqrs.Request):
    message_id: uuid.UUID
    emoji: typing.Text
    count: pydantic.PositiveInt


class MessageInfo(cqrs.Request):
    chat_id: uuid.UUID
    message_id: uuid.UUID
    sender: typing.Text
    content: typing.Text
    attachments: typing.List[get_attachments.AttachmentInfo]
    reactions: typing.List[ReactionsUnderMessage]
    reply_to: typing.Optional[uuid.UUID]
    read: pydantic.StrictBool
    created: datetime.datetime
    updated: datetime.datetime


class Messages(cqrs.Response):
    messages: typing.List[MessageInfo] = pydantic.Field(default_factory=list)
    next_message_id: typing.Optional[uuid.UUID]
    prev_message_id: typing.Optional[uuid.UUID]


class GetMessagePreview(cqrs.Request):
    message_id: uuid.UUID
    account: typing.Text


class MessagePreview(cqrs.Response):
    chat_id: uuid.UUID
    message_id: uuid.UUID
    sender: typing.Text
    content: typing.Text
    created: datetime.datetime
