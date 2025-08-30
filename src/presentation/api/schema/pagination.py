import typing

import pydantic

Item = typing.TypeVar("Item")


def slice_items(
    items: typing.Sequence[Item],
    limit: int,
    offset: int,
) -> typing.Sequence[Item]:
    return items[offset : offset + limit]


class Pagination(pydantic.BaseModel, typing.Generic[Item]):
    _pagination_params: typing.ClassVar[str] = "&limit={limit}&offset={offset}"

    url: pydantic.StrictStr = pydantic.Field(exclude=True)
    base_items: typing.Sequence[Item] = pydantic.Field(
        default_factory=list,
        frozen=True,
        exclude=True,
    )
    limit: pydantic.NonNegativeInt = pydantic.Field(default=10, frozen=True)
    offset: pydantic.NonNegativeInt = pydantic.Field(default=0, frozen=True)
    count: pydantic.NonNegativeInt = pydantic.Field(default=0, frozen=True)

    def _combine_url(
        self,
        limit: pydantic.NonNegativeInt,
        offset: pydantic.NonNegativeInt,
    ) -> str:
        return (self.url + self._pagination_params).format(
            limit=limit,
            offset=offset,
        )

    @pydantic.computed_field()
    @property
    def items(self) -> typing.Sequence[Item]:
        return slice_items(
            items=self.base_items,
            limit=self.limit,
            offset=self.offset,
        )

    @pydantic.computed_field()
    @property
    def next(self) -> pydantic.StrictStr | None:
        if len(self.items) < self.limit:
            return None

        return self._combine_url(
            limit=self.limit,
            offset=self.offset + self.limit,
        )

    @pydantic.computed_field()
    @property
    def previous(self) -> pydantic.StrictStr | None:
        if self.offset - self.limit < 0:
            return None

        return self._combine_url(
            limit=self.limit,
            offset=self.offset - self.limit,
        )


class MessagesPaginator(Pagination, typing.Generic[Item]):
    limit: pydantic.NonNegativeInt = pydantic.Field(default=0, exclude=True)
    offset: pydantic.NonNegativeInt = pydantic.Field(default=0, exclude=True)

    next_id: pydantic.UUID4 | None = None
    previous_id: pydantic.UUID4 | None = None
    reverse: pydantic.StrictBool = pydantic.Field(default=False, exclude=False)

    @pydantic.computed_field()
    @property
    def next(self) -> str | None:
        if self.next_id is None:
            return None
        return self.url + f"?last_message_id={self.next_id}&reverse={str(self.reverse).lower()}"

    @pydantic.computed_field()
    @property
    def previous(self) -> str | None:
        if self.previous_id is None:
            return None
        return self.url + f"?last_message_id={self.previous_id}&reverse={str(self.reverse).lower()}"
