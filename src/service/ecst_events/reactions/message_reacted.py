import typing
import uuid

import cqrs
import pydantic


class MessageReactedPayload(pydantic.BaseModel):
    chat_id: uuid.UUID
    message_id: uuid.UUID
    reactor: typing.Text
    emoji: typing.Text


class MessageReactedECST(cqrs.ECSTEvent[MessageReactedPayload], frozen=True):
    pass
