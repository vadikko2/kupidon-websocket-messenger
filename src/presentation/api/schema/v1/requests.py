import typing

import pydantic

from presentation.api.schema import constants, validators


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


class PostMessage(pydantic.BaseModel, frozen=True):
    reply_to: typing.Optional[pydantic.UUID4] = pydantic.Field(
        description="Message ID to reply to",
        default=None,
    )
    content: typing.Optional[typing.Text] = pydantic.Field(
        description="Message content",
        examples=["Hello World!"],
        min_length=constants.MIN_MESSAGE_LENGTH,
        max_length=constants.MAX_MESSAGE_LENGTH,
        json_schema_extra={"nullable": True},
        frozen=True,
        default=None,
    )
    attachments: typing.List[pydantic.UUID4] = pydantic.Field(
        description="Attachments IDs",
        default_factory=list,
        max_length=5,
    )

    @pydantic.model_validator(mode="after")
    def check_content(self):
        if self.content is None and not self.attachments:
            raise ValueError("Message should have content or attachments")
        return self
