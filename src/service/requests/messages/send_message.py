import datetime
import typing

import cqrs
import pydantic


class SendMessage(cqrs.Request):
    chat_id: pydantic.UUID4
    sender: typing.Text

    reply_to: typing.Optional[pydantic.UUID4] = None

    content: typing.Optional[typing.Text] = None
    attachments: typing.List[pydantic.UUID4]


class MessageSent(cqrs.Response):
    message_id: pydantic.UUID4
    created: datetime.datetime
