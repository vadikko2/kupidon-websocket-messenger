import datetime
import typing
import uuid

import pydantic

from domain import message


class MessageSent(pydantic.BaseModel):
    message_id: uuid.UUID
    receiver: typing.Text
    timestamp: datetime.datetime


class HistoryPage(pydantic.BaseModel):
    _history_page_url: typing.ClassVar[str] = (
        "/history/{partner}?limit={limit}&latest={latest}"
    )

    partner: typing.Text
    messages: typing.List[message.Message] = pydantic.Field(default_factory=list)

    limit: pydantic.NonNegativeInt
    latest_id: uuid.UUID | None

    @pydantic.computed_field()
    def next_page(self) -> str | None:
        if self.latest_id is None:
            return None

        return self._history_page_url.format(
            partner=self.partner,
            limit=self.limit,
            latest=self.latest_id,
        )

    @pydantic.computed_field()
    def count(self) -> pydantic.NonNegativeInt:
        return len(self.messages)
