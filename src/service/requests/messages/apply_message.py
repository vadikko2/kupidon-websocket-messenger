import typing

import cqrs
import pydantic


class ApplyMessage(cqrs.Request):
    applier: typing.Text

    message_id: pydantic.UUID4
