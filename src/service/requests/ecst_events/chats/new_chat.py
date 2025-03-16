import typing
import uuid

import pydantic


class AddedIntoChatPayload(pydantic.BaseModel, frozen=True):
    chat_id: uuid.UUID
    account_id: typing.Text
    invited_by: typing.Text
