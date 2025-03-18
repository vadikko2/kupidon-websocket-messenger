import typing
import uuid

import cqrs


class ApplyMessage(cqrs.Request):
    applier: typing.Text

    message_id: uuid.UUID
