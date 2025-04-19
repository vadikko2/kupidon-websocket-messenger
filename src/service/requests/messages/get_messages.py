import datetime
import typing

import cqrs
import pydantic

from service.requests.attachments import get_attachments


class GetMessages(cqrs.Request):
    chat_id: pydantic.UUID4
    account: typing.Text
    messages_limit: pydantic.NonNegativeInt
    latest_message_id: typing.Optional[pydantic.UUID4] = None
    reverse: pydantic.StrictBool = False


class ReactionsUnderMessage(cqrs.Request):
    message_id: pydantic.UUID4
    emoji: typing.Text
    count: pydantic.PositiveInt


class MessageInfo(cqrs.Request):
    chat_id: pydantic.UUID4
    message_id: pydantic.UUID4
    sender: typing.Text
    content: typing.Optional[typing.Text]
    attachments: typing.List[get_attachments.AttachmentInfo]
    reactions: typing.List[ReactionsUnderMessage]
    reply_to: typing.Optional["MessagePreview"]
    read: pydantic.StrictBool
    created: datetime.datetime
    updated: datetime.datetime


class Messages(cqrs.Response):
    messages: typing.List[MessageInfo] = pydantic.Field(default_factory=list)
    next_message_id: typing.Optional[pydantic.UUID4]
    prev_message_id: typing.Optional[pydantic.UUID4]


class GetMessagePreview(cqrs.Request):
    message_id: pydantic.UUID4
    account: typing.Text


class MessagePreview(cqrs.Response):
    chat_id: pydantic.UUID4
    message_id: pydantic.UUID4
    sender: typing.Text
    content: typing.Optional[typing.Text]
    created: datetime.datetime
