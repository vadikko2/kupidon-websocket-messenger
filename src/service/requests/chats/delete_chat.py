import typing

import cqrs
import pydantic


class DeleteChat(cqrs.Request):
    actor: typing.Text
    chat_id: pydantic.UUID4
