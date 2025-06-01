import enum

import pydantic


class ImageTypes(enum.StrEnum):
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"


class ImageMeta(pydantic.BaseModel):
    height: pydantic.NonNegativeInt
    width: pydantic.NonNegativeInt

    image_type: ImageTypes
