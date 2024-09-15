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


class NewMessageAdded(cqrs.ECSTEvent[MessageAddedPayload], frozen=True):
    pass


class ReactionAddedPayload(pydantic.BaseModel):
    chat_id: uuid.UUID
    message_id: uuid.UUID
    reactor: typing.Text
    emoji: typing.Text


class NewReactionAdded(cqrs.ECSTEvent[ReactionAddedPayload], frozen=True):
    pass
