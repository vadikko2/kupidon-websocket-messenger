import typing
import uuid

import cqrs


class UnreactMessage(cqrs.Request):
    unreactor: typing.Text
    reaction: typing.Text
    message_id: uuid.UUID
