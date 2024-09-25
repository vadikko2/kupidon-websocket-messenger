import uuid

import cqrs
import pydantic


class MessageDeletedPayload(pydantic.BaseModel):
    chat_id: uuid.UUID
    message_id: uuid.UUID


class MessageDeletedECST(cqrs.ECSTEvent[MessageDeletedPayload], frozen=True):
    pass
