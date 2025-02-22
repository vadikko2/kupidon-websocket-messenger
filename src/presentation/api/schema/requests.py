import typing

import pydantic

from presentation.api.schema import validators


class Reaction(pydantic.BaseModel, frozen=True):
    emoji: typing.Text = pydantic.Field(
        max_length=1,
        min_length=1,
        examples=["👍", "👎", "❤️"],
    )

    @pydantic.field_validator("emoji")
    def check_emoji(cls, value):
        return validators.emoji_validator(value)
