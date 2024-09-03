import datetime
import typing
import uuid

import pydantic

from domain import messages as messages_entity


class MessageSent(pydantic.BaseModel):
    message_id: uuid.UUID
    timestamp: datetime.datetime


class ChatCreated(pydantic.BaseModel):
    chat_id: uuid.UUID


class ChatInfo(pydantic.BaseModel):
    chat_id: uuid.UUID
    name: typing.Text | None
    last_activity_timestamp: typing.Optional[datetime.datetime]
    last_message_id: uuid.UUID | None


class ChatList(pydantic.BaseModel):
    _next_page: typing.ClassVar[str] = "/chats/?limit={limit}?offset={offset}"

    chats: typing.List[ChatInfo] = pydantic.Field(default_factory=list)
    limit: pydantic.NonNegativeInt
    offset: pydantic.NonNegativeInt

    @pydantic.computed_field()
    def next_page(self) -> str | None:
        if not len(self.chats):
            return None
        return self._next_page.format(
            limit=self.limit,
            offset=self.offset + self.count,  # type: ignore
        )

    @pydantic.computed_field()
    def count(self) -> pydantic.NonNegativeInt:
        return len(self.chats)


class HistoryPage(pydantic.BaseModel):
    _next_page: typing.ClassVar[str] = (
        "/history/{chat_id}?limit={limit}&latest={latest}"
    )

    chat_id: uuid.UUID
    messages: typing.List[messages_entity.Message] = pydantic.Field(
        default_factory=list,
    )

    limit: pydantic.NonNegativeInt
    latest_id: uuid.UUID | None

    @pydantic.computed_field()
    def next_page(self) -> str | None:
        if self.latest_id is None or not len(self.messages):
            return None

        return self._next_page.format(
            chat_id=self.chat_id,
            limit=self.limit,
            latest=self.latest_id,
        )

    @pydantic.computed_field()
    def count(self) -> pydantic.NonNegativeInt:
        return len(self.messages)
