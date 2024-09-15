import typing
import uuid

import cqrs


class DeleteMessage(cqrs.Request):
    message_id: uuid.UUID
    deleter: typing.Text
