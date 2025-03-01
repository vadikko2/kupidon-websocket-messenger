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


class CreateChat(pydantic.BaseModel, frozen=True):
    name: typing.Text = pydantic.Field(
        min_length=1,
        max_length=100,
        description="Chat name",
        examples=["Untitled"],
    )
    participants: typing.List[typing.Text] = pydantic.Field(
        description="Participants IDs",
        examples=[["account-id-1", "account-id-2"]],
    )
    avatar: typing.Optional[pydantic.AnyHttpUrl] = pydantic.Field(
        default=None,
        description="URL to avatar image",
    )
