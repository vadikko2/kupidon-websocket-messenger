import typing
import uuid

import cqrs


class DeleteChat(cqrs.Request):
    actor: typing.Text
    chat_id: uuid.UUID
