import enum

import pydantic


class ImageTypes(enum.StrEnum):
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"


class ImageMeta(pydantic.BaseModel):
    height: pydantic.NonNegativeInt
    width: pydantic.NonNegativeInt

    url_100x100: str
    url_200x200: str

    image_type: ImageTypes

    blurhash: str | None = None
