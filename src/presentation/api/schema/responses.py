import datetime
import uuid

import pydantic


class MessageSent(pydantic.BaseModel):
    message_id: uuid.UUID
    timestamp: datetime.datetime


class ChatCreated(pydantic.BaseModel):
    chat_id: uuid.UUID
