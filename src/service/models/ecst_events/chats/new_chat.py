import pydantic


class AddedIntoChatPayload(pydantic.BaseModel, frozen=True):
    chat_id: pydantic.UUID4
    account_id: str
    invited_by: str
