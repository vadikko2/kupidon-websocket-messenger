import pydantic


class MessageUnreactedPayload(pydantic.BaseModel):
    chat_id: pydantic.UUID4
    message_id: pydantic.UUID4
    reaction_id: pydantic.UUID4
