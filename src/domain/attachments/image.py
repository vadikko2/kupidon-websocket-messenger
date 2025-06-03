import enum
import typing

import pydantic


class ImageTypes(enum.StrEnum):
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"


class ImageMeta(pydantic.BaseModel):
    height: pydantic.NonNegativeInt
    width: pydantic.NonNegativeInt

    url_100x100: typing.Text
    url_200x200: typing.Text

    image_type: ImageTypes
