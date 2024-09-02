import typing
import uuid

import pydantic

from domain import message


class Attachment(pydantic.BaseModel):
    name: typing.Text = pydantic.Field(max_length=100, default_factory=uuid.uuid4)
    url: pydantic.AnyUrl
    content_type: message.AttachmentType
