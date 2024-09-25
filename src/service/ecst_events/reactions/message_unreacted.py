import uuid

import cqrs
import pydantic


class MessageUnreactedPayload(pydantic.BaseModel):
    chat_id: uuid.UUID
    message_id: uuid.UUID
    reaction_id: uuid.UUID


class MessageUnreactedECST(cqrs.ECSTEvent[MessageUnreactedPayload], frozen=True):
    pass
