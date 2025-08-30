import cqrs
import pydantic


class ApplyMessage(cqrs.Request):
    applier: str

    message_id: pydantic.UUID4
