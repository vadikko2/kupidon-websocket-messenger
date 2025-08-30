import datetime

import cqrs
import pydantic


class SendMessage(cqrs.Request):
    chat_id: pydantic.UUID4
    sender: str

    reply_to: pydantic.UUID4 | None = None

    content: str | None = None
    attachments: list[pydantic.UUID4]


class MessageSent(cqrs.Response):
    message_id: pydantic.UUID4
    created: datetime.datetime
