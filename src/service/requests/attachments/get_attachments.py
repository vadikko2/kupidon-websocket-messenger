import datetime
import typing

import cqrs
import pydantic

from domain import attachments


class GetAttachments(cqrs.Request):
    chat_id: pydantic.UUID4
    account_id: typing.Text
    limit: pydantic.NonNegativeInt
    offset: pydantic.NonNegativeInt


class AttachmentInfo(pydantic.BaseModel):
    attachment_id: pydantic.UUID4
    chat_id: pydantic.UUID4
    urls: typing.Sequence[pydantic.AnyHttpUrl]
    uploaded: datetime.datetime
    content_type: attachments.AttachmentType


class Attachments(cqrs.Response):
    attachments: typing.List[AttachmentInfo]
