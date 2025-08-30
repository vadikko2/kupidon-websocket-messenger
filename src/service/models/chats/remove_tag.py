import cqrs
import pydantic


class RemoveTag(cqrs.Request):
    chat_id: pydantic.UUID4
    account_id: str
    tag: pydantic.StrictStr
