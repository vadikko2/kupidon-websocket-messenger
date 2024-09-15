import typing
import uuid

import cqrs


class UnreactMessage(cqrs.Request):
    unreactor: typing.Text
    reaction_id: uuid.UUID
    message_id: uuid.UUID
