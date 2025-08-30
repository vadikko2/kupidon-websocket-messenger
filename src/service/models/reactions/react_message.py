import cqrs
import pydantic


class ReactMessage(cqrs.Request):
    reactor: str
    message_id: pydantic.UUID4
    emoji: str
