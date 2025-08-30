import cqrs
import pydantic


class DeleteMessage(cqrs.Request):
    message_id: pydantic.UUID4
    deleter: str
