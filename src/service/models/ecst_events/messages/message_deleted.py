import pydantic


class MessageDeletedPayload(pydantic.BaseModel):
    chat_id: pydantic.UUID4
    message_id: pydantic.UUID4
