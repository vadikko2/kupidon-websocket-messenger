import datetime

import pydantic


class MessageAddedPayload(pydantic.BaseModel):
    chat_id: pydantic.UUID4
    message_id: pydantic.UUID4

    sender: str
    content: str | None
    reply_to: pydantic.UUID4 | None

    created: datetime.datetime
