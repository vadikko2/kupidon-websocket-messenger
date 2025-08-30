import pydantic

from domain import messages


class ChatTag(pydantic.BaseModel):
    tag: str

    def __eq__(self, other):
        if not isinstance(other, ChatTag):
            return False
        return self.tag == other.tag

    def __hash__(self):
        return hash(self.tag)


class Participant(pydantic.BaseModel):
    """
    Participant entity
    """

    account_id: str = pydantic.Field(frozen=True)
    initiated_by: str = pydantic.Field(frozen=True)
    tags: set[ChatTag] = pydantic.Field(default_factory=set)

    last_read_message: messages.Message | None = pydantic.Field(default=None)

    def set_last_read_message(self, message: messages.Message):
        self.last_read_message = message

    def add_tag(self, tag: ChatTag):
        self.tags.add(tag)

    def remove_tag(self, tag: ChatTag):
        self.tags.remove(tag)

    def __eq__(self, other):
        if not isinstance(other, Participant):
            return False
        return self.account_id == other.account_id

    def __hash__(self):
        return hash(self.account_id)

    def __repr__(self):
        return self.account_id

    def __str__(self):
        return self.account_id
