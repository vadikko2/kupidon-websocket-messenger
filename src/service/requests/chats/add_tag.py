import typing

import cqrs
import pydantic


class AddTag(cqrs.Request):
    chat_id: pydantic.UUID4
    account_id: typing.Text
    tag: pydantic.StrictStr
