import typing

import cqrs
import pydantic

from domain import attachments


class UploadAttachment(cqrs.Request):
    chat_id: pydantic.UUID4
    uploader: typing.Text
    filename: typing.Text
    content_type: attachments.AttachmentType
    content: bytes = pydantic.Field(exclude=True)


class AttachmentUploaded(cqrs.Response):
    attachment_id: pydantic.UUID4
    urls: typing.List[pydantic.AnyHttpUrl] = pydantic.Field(min_length=1)
