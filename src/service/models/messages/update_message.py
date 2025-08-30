import datetime

import cqrs
import pydantic


class UpdateMessage(cqrs.Request):
    chat_id: pydantic.UUID4
    message_id: pydantic.UUID4

    updater: str
    content: str | None
    attachments: list[pydantic.UUID4]


class MessageUpdated(cqrs.Response):
    chat_id: pydantic.UUID4
    message_id: pydantic.UUID4

    updated_at: datetime.datetime
