import cqrs
import pydantic


class OpenChat(cqrs.Request):
    initiator: str
    participants: list[str]
    name: str
    avatar: str | None = pydantic.Field(default=None)


class ChatOpened(cqrs.Response):
    chat_id: pydantic.UUID4
