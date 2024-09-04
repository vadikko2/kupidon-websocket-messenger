import typing
import uuid

import cqrs

from domain import messages


class ApplyMessage(cqrs.Request):
    applier: typing.Text

    message_id: uuid.UUID
    status: messages.MessageStatus
