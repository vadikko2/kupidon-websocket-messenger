import cqrs
import pydantic


class UnreactMessage(cqrs.Request):
    unreactor: str
    reaction: str
    message_id: pydantic.UUID4
