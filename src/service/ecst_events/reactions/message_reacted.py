import typing
import uuid

import pydantic


class MessageReactedPayload(pydantic.BaseModel):
    chat_id: uuid.UUID
    message_id: uuid.UUID
    reactor: typing.Text
    emoji: typing.Text
