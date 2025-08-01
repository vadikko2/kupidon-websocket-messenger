import typing

import pydantic


class MessageReadPayload(pydantic.BaseModel):
    chat_id: pydantic.UUID4
    message_id: pydantic.UUID4

    reader: typing.Text
