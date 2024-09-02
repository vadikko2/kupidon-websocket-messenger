import datetime
import enum
import typing
import uuid

import pydantic


class MessageStatus(enum.IntEnum):
    SENT = 1
    RECEIVED = 2
    DELIVERED = 3
    READ = 4
    DELETED = 5


class Attachment(pydantic.BaseModel, frozen=True):
    attachment_id: uuid.UUID
    url: pydantic.AnyUrl
    name: typing.Optional[typing.Text] = pydantic.Field(default=None, max_length=100)


class Message(pydantic.BaseModel):
    message_id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4, frozen=True)

    sender: typing.Text = pydantic.Field(frozen=True)
    receiver: typing.Text pydantic.Field(frozen=True)

    content: typing.Text pydantic.Field(frozen=True)
    attachments: typing.List[Attachment] = pydantic.Field(default_factory=list, max_length=5, frozen=True)
    status: MessageStatus = pydantic.Field(default=MessageStatus.SENT)

    created: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.utcnow, frozen=True)
    updated: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.utcnow)
