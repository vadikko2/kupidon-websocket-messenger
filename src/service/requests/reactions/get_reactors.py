import typing
import uuid

import cqrs
import pydantic


class GetReactors(cqrs.Request):
    message_id: uuid.UUID
    emoji: typing.Text = pydantic.Field(
        max_length=1,
        min_length=1,
        examples=["👍", "👎", "❤️"],
    )


class Reactors(cqrs.Response):
    reactors: typing.Sequence[typing.Text]
