import uuid

import pydantic


class MessageDeletedPayload(pydantic.BaseModel):
    chat_id: uuid.UUID
    message_id: uuid.UUID
