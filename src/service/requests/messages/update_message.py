import datetime
import typing

import cqrs
import pydantic


class UpdateMessage(cqrs.Request):
    chat_id: pydantic.UUID4
    message_id: pydantic.UUID4

    updater: typing.Text
    content: typing.Optional[typing.Text]
    attachments: typing.List[pydantic.UUID4]


class MessageUpdated(cqrs.Response):
    chat_id: pydantic.UUID4
    message_id: pydantic.UUID4

    updated_at: datetime.datetime
