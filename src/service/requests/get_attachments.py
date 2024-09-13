import datetime
import typing
import uuid

import cqrs
import pydantic

from domain import attachments


class GetAttachments(cqrs.Request):
    chat_id: uuid.UUID
    account_id: typing.Text
    limit: pydantic.NonNegativeInt
    offset: pydantic.NonNegativeInt


class Attachment(pydantic.BaseModel):
    attachment_id: uuid.UUID
    url: pydantic.AnyHttpUrl
    uploaded: datetime.datetime
    content_type: attachments.AttachmentType


class Attachments(cqrs.Response):
    chat_id: uuid.UUID
    attachments: typing.List[Attachment]
