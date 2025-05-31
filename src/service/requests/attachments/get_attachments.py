import datetime
import typing

import cqrs
import pydantic

from domain import attachments


class GetAttachments(cqrs.Request):
    chat_id: pydantic.UUID4
    account_id: typing.Text

    type_filter: typing.List[attachments.AttachmentType] = pydantic.Field(default_factory=list)
    attachment_id_filter: typing.List[pydantic.UUID4] = pydantic.Field(default_factory=list)

    limit: pydantic.NonNegativeInt
    offset: pydantic.NonNegativeInt


class AttachmentInfo(pydantic.BaseModel):
    attachment_id: pydantic.UUID4
    chat_id: pydantic.UUID4
    urls: typing.Sequence[pydantic.AnyHttpUrl]
    uploaded: datetime.datetime
    content_type: attachments.AttachmentType

    meta: typing.Dict[pydantic.StrictStr, typing.Any] = pydantic.Field(default_factory=dict)


class Attachments(cqrs.Response):
    attachments: typing.List[AttachmentInfo]
