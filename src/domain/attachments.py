import datetime
import enum
import typing
import uuid

import pydantic


class AttachmentType(enum.StrEnum):
    """
    Attachment types
    """

    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"


class Attachment(pydantic.BaseModel, frozen=True):
    """
    Attachment entity
    """

    attachment_id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)

    chat_id: uuid.UUID
    uploader: typing.Text

    uploaded: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)

    urls: typing.List[pydantic.AnyHttpUrl]
    filename: typing.Optional[typing.Text] = pydantic.Field(
        default=None,
        max_length=100,
    )
    content_type: AttachmentType

    def __hash__(self):
        return str(hash(self.attachment_id))
