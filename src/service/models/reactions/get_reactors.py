import typing

import cqrs
import pydantic


class GetReactors(cqrs.Request):
    message_id: pydantic.UUID4
    emoji: str = pydantic.Field(
        max_length=1,
        min_length=1,
        examples=["👍", "👎", "❤️"],
    )


class Reactors(cqrs.Response):
    reactors: typing.Sequence[str]
