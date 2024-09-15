import typing
import uuid

import cqrs


class ReactMessage(cqrs.Request):
    reactor: typing.Text
    message_id: uuid.UUID
    emoji: typing.Text
