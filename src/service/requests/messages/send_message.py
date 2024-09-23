import datetime
import typing
import uuid

import cqrs


class SendMessage(cqrs.Request):
    chat_id: uuid.UUID
    sender: typing.Text

    reply_to: typing.Optional[uuid.UUID] = None

    content: typing.Text
    attachments: typing.List[uuid.UUID]


class MessageSent(cqrs.Response):
    message_id: uuid.UUID
    created: datetime.datetime
