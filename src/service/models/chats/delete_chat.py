import cqrs
import pydantic


class DeleteChat(cqrs.Request):
    actor: str
    chat_id: pydantic.UUID4
