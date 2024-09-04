import typing
import uuid

import cqrs


class ApplyMessageRead(cqrs.Request):
    reader: typing.Text
    message_id: uuid.UUID


class ApplyMessageReceive(cqrs.Request):
    receiver: typing.Text
    message_id: uuid.UUID
