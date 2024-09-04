import typing
import uuid

import cqrs


class DeleteMessage(cqrs.Request):
    deleter: typing.Text
    message_id: uuid.UUID
