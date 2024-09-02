import datetime
import enum
import typing
import uuid

import pydantic


class MessageStatus(enum.IntEnum):
    SENT = 1
    RECEIVED = 2
    READ = 3


class Attachment(pydantic.BaseModel, frozen=True):
    attachment_id: uuid.UUID
    url: pydantic.AnyUrl
    name: typing.Optional[typing.Text] = pydantic.Field(default=None, max_length=100)


class Message(pydantic.BaseModel, frozen=True):
    message_id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
    sender: typing.Text
    receiver: typing.Text
    content: typing.Text
    attachments: typing.List[Attachment] = pydantic.Field(default_factory=list, max_length=5)
    status: MessageStatus = pydantic.Field(default=MessageStatus.SENT)
    timestamp: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.utcnow)
