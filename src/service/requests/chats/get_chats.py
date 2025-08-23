import datetime
import typing

import cqrs
import pydantic


class GetChats(cqrs.Request):
    participant: typing.Text
    chat_ids: typing.List[pydantic.UUID4] | None = None
    with_participant_ids: typing.List[typing.Text] | None = None
    strict_participants_search: pydantic.StrictBool = False


class ChatInfo(cqrs.Response):
    chat_id: pydantic.UUID4
    name: typing.Text
    avatar: typing.Optional[pydantic.AnyHttpUrl] = None
    tags: typing.List[typing.Text] = pydantic.Field(default_factory=list)
    participants_count: pydantic.NonNegativeInt
    last_activity_timestamp: typing.Optional[datetime.datetime]
    last_message_id: typing.Optional[pydantic.UUID4] = None
    last_read_message_id: typing.Optional[pydantic.UUID4] = None
    not_read_messages_count: pydantic.NonNegativeInt = pydantic.Field(
        description="Count of not read messages",
        default=0,
    )


class Chats(cqrs.Response):
    chats: typing.Sequence[ChatInfo]
