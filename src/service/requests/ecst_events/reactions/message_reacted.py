import typing

import pydantic


class MessageReactedPayload(pydantic.BaseModel):
    chat_id: pydantic.UUID4
    message_id: pydantic.UUID4
    reactor: typing.Text
    emoji: typing.Text
