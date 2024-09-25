import datetime
import typing
import uuid

import cqrs
import pydantic


class MessageAddedPayload(pydantic.BaseModel):
    chat_id: uuid.UUID
    message_id: uuid.UUID

    sender: typing.Text
    content: typing.Text
    reply_to: typing.Optional[uuid.UUID]

    created: datetime.datetime


class NewMessageAddedECST(cqrs.ECSTEvent[MessageAddedPayload], frozen=True):
    pass
