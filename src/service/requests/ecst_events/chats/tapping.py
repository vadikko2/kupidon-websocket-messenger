import typing
import uuid

import pydantic


class TappingInChatPayload(pydantic.BaseModel):
    chat_id: uuid.UUID
    account_id: typing.Text
