import cqrs
import pydantic


class OpenChat(cqrs.Request):
    initiator: str
    participants: list[str]
    first_writers: list[str] | None = None
    name: str
    avatar: str | None = pydantic.Field(default=None)
    welcome_message: str | None = pydantic.Field(default=None)


class ChatOpened(cqrs.Response):
    chat_id: pydantic.UUID4
