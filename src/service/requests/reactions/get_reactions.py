import typing
import uuid

import cqrs


class GetReactors(cqrs.Request):
    message_id: uuid.UUID
    emoji: typing.Text


class Reactors(cqrs.Response):
    pass
