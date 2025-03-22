import typing

import pydantic


class AddedIntoChatPayload(pydantic.BaseModel, frozen=True):
    chat_id: pydantic.UUID4
    account_id: typing.Text
    invited_by: typing.Text
