import pydantic

from presentation.api.schema import constants, validators


class Reaction(pydantic.BaseModel, frozen=True):
    emoji: pydantic.StrictStr = pydantic.Field(
        max_length=1,
        min_length=1,
        examples=["👍", "👎", "❤️"],
    )

    @pydantic.field_validator("emoji")
    def check_emoji(cls, value):
        return validators.emoji_validator(value)


class CreateChat(pydantic.BaseModel, frozen=True):
    name: pydantic.StrictStr = pydantic.Field(
        min_length=1,
        max_length=100,
        description="Chat name",
        examples=["Untitled"],
    )
    participants: list[pydantic.StrictStr] = pydantic.Field(
        description="Participants IDs",
        examples=[["account-id-1", "account-id-2"]],
    )
    avatar: pydantic.AnyHttpUrl | None = pydantic.Field(
        default=None,
        description="URL to avatar image",
    )
    welcome_message: pydantic.StrictStr | None = pydantic.Field(
        default=None,
        description="Welcome message",
        examples=["Hello World!"],
        min_length=constants.MIN_MESSAGE_LENGTH,
        max_length=constants.MAX_MESSAGE_LENGTH,
        json_schema_extra={"nullable": True},
    )


class PostMessage(pydantic.BaseModel, frozen=True):
    reply_to: pydantic.UUID4 | None = pydantic.Field(
        description="Message ID to reply to",
        default=None,
    )
    content: pydantic.StrictStr | None = pydantic.Field(
        description="Message content",
        examples=["Hello World!"],
        min_length=constants.MIN_MESSAGE_LENGTH,
        max_length=constants.MAX_MESSAGE_LENGTH,
        json_schema_extra={"nullable": True},
        default=None,
    )
    attachments: list[pydantic.UUID4] = pydantic.Field(
        description="Attachments IDs",
        default_factory=list,
        max_length=5,
    )

    @pydantic.model_validator(mode="after")
    def check_content(self):
        if self.content is None and not self.attachments:
            raise ValueError("Message should have content or attachments")
        return self


class UpdateMessage(pydantic.BaseModel, frozen=True):
    message_id: pydantic.UUID4 = pydantic.Field(
        description="Message ID",
    )
    content: pydantic.StrictStr | None = pydantic.Field(
        description="Message content",
        examples=["Hello World!"],
        min_length=constants.MIN_MESSAGE_LENGTH,
        max_length=constants.MAX_MESSAGE_LENGTH,
        json_schema_extra={"nullable": True},
        frozen=True,
        default=None,
    )
    attachments: list[pydantic.UUID4] = pydantic.Field(
        description="Attachments IDs",
        default_factory=list,
        max_length=5,
    )


class ChatTag(pydantic.BaseModel, frozen=True):
    tag: pydantic.StrictStr = pydantic.Field(
        min_length=1,
        max_length=10,
        examples=["tag-1", "tag-2"],
    )
