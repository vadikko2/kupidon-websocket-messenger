import typing

import pydantic

Item = typing.TypeVar("Item")


def slice_items(
    items: typing.Sequence[Item],
    limit: pydantic.NonNegativeInt,
    offset: pydantic.NonNegativeInt,
) -> typing.Sequence[Item]:
    return items[offset : offset + limit]


class Pagination(pydantic.BaseModel, typing.Generic[Item]):
    _pagination_params: typing.ClassVar[typing.Text] = "&limit={limit}&offset={offset}"

    url: typing.Text = pydantic.Field(exclude=True)
    base_items: typing.Sequence[Item] = pydantic.Field(
        default_factory=list,
        frozen=True,
        exclude=True,
    )
    limit: pydantic.NonNegativeInt = pydantic.Field(default=10, frozen=True)
    offset: pydantic.NonNegativeInt = pydantic.Field(default=0, frozen=True)

    def _combine_url(
        self,
        limit: pydantic.NonNegativeInt,
        offset: pydantic.NonNegativeInt,
    ) -> typing.Text:
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
    def next(self) -> typing.Text | None:
        if len(self.items) < self.limit:
            return None

        return self._combine_url(
            limit=self.limit,
            offset=self.offset + self.limit,
        )

    @pydantic.computed_field()
    @property
    def previous(self) -> typing.Text | None:
        if self.offset - self.limit < 0:
            return None

        return self._combine_url(
            limit=self.limit,
            offset=self.offset - self.limit,
        )

    @pydantic.computed_field()
    @property
    def count(self) -> pydantic.NonNegativeInt:
        return len(self.base_items)
