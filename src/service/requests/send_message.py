import datetime
import typing
import uuid

import cqrs
import pydantic

from domain import messages


class Attachment(pydantic.BaseModel, frozen=True):
    url: pydantic.AnyUrl
    name: typing.Optional[typing.Text]
    content_type: messages.AttachmentType


class SendMessage(cqrs.Request):
    chat_id: uuid.UUID
    sender: typing.Text

    reply_to: typing.Optional[uuid.UUID] = None

    content: typing.Text
    attachments: typing.List[Attachment]


class MessageSent(cqrs.Response):
    message_id: uuid.UUID
    created: datetime.datetime
