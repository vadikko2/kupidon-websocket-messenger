import typing
import uuid

import cqrs
import pydantic


class AttachmentUploaded(cqrs.Response):
    attachment_id: uuid.UUID
    urls: typing.List[pydantic.AnyHttpUrl] = pydantic.Field(min_length=1)
