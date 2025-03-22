import typing

import cqrs
import pydantic


class ReactMessage(cqrs.Request):
    reactor: typing.Text
    message_id: pydantic.UUID4
    emoji: typing.Text
