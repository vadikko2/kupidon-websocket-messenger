import typing

import cqrs
import pydantic

from domain import chats


class GetChats(cqrs.Request):
    participant: typing.Text
    limit: pydantic.NonNegativeInt
    offset: pydantic.NonNegativeInt


class Chats(cqrs.Response):
    chats: typing.List[chats.Chat]
