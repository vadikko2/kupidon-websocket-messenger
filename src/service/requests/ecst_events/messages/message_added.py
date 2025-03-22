import datetime
import typing

import pydantic


class MessageAddedPayload(pydantic.BaseModel):
    chat_id: pydantic.UUID4
    message_id: pydantic.UUID4

    sender: typing.Text
    content: typing.Text
    reply_to: typing.Optional[pydantic.UUID4]

    created: datetime.datetime
