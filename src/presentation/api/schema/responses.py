import datetime
import typing
import uuid

import pydantic


class MessageSent(pydantic.BaseModel):
    message_id: uuid.UUID
    receiver: typing.Text
    timestamp: datetime.datetime
