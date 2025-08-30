import datetime
import typing

import cqrs
import pydantic


class GetChats(cqrs.Request):
    participant: str
    chat_ids: list[pydantic.UUID4] | None = None
    with_participant_ids: list[str] | None = None
    strict_participants_search: bool = False


class ChatInfo(cqrs.Response):
    chat_id: pydantic.UUID4
    name: str
    avatar: str | None = None
    tags: list[str] = pydantic.Field(default_factory=list)
    participant_ids: list[str]
    last_activity_timestamp: datetime.datetime | None
    last_message_id: pydantic.UUID4 | None = None
    last_read_message_id: pydantic.UUID4 | None = None
    not_read_messages_count: int = pydantic.Field(
        description="Count of not read messages",
        default=0,
    )

    @pydantic.computed_field()
    def participants_count(self) -> int:
        return len(self.participant_ids)


class Chats(cqrs.Response):
    chats: typing.Sequence[ChatInfo]
