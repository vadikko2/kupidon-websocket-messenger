import cqrs
import pydantic


class UploadImage(cqrs.Request):
    chat_id: pydantic.UUID4
    uploader: str

    content: bytes = pydantic.Field(exclude=True)
    width: pydantic.PositiveInt
    height: pydantic.PositiveInt


class ImageUploaded(cqrs.Response):
    attachment_id: pydantic.UUID4
    attachment_urls: list[str]

    blurhash: str
