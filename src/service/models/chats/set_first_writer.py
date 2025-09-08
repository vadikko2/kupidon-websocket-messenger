import cqrs
import pydantic


class SetFirstWriter(cqrs.Request):
    chat_id: pydantic.UUID4
    account_id: str
    first_writer: bool
