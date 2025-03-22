import datetime

import pydantic


class MessageSent(pydantic.BaseModel):
    message_id: pydantic.UUID4
    timestamp: datetime.datetime


class ChatCreated(pydantic.BaseModel):
    chat_id: pydantic.UUID4
