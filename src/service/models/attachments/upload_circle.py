import cqrs
import pydantic

from domain import attachments


class UploadCircle(cqrs.Request):
    chat_id: pydantic.UUID4
    uploader: str

    circle_format: attachments.CircleTypes

    content: bytes = pydantic.Field(exclude=True)
    duration_milliseconds: pydantic.NonNegativeInt


class CircleUploaded(cqrs.Response):
    attachment_id: pydantic.UUID4
    attachment_url: str
