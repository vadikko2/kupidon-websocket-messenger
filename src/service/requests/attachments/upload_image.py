import typing

import cqrs
import pydantic


class UploadImage(cqrs.Request):
    chat_id: pydantic.UUID4
    uploader: typing.Text

    content: bytes = pydantic.Field(exclude=True)
    width: pydantic.PositiveInt
    height: pydantic.PositiveInt


class ImageUploaded(cqrs.Response):
    attachment_id: pydantic.UUID4
    attachment_urls: typing.List[typing.Text]
