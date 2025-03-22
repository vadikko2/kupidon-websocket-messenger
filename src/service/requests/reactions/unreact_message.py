import typing

import cqrs
import pydantic


class UnreactMessage(cqrs.Request):
    unreactor: typing.Text
    reaction: typing.Text
    message_id: pydantic.UUID4
