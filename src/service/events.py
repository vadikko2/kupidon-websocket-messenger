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


class MessageReactedPayload(pydantic.BaseModel):
    chat_id: uuid.UUID
    message_id: uuid.UUID
    reactor: typing.Text
    emoji: typing.Text


class MessageReactedECST(cqrs.ECSTEvent[MessageReactedPayload], frozen=True):
    pass


class MessageUnreactedPayload(pydantic.BaseModel):
    chat_id: uuid.UUID
    message_id: uuid.UUID
    reaction_id: uuid.UUID


class MessageUnreactedECST(cqrs.ECSTEvent[MessageUnreactedPayload], frozen=True):
    pass
