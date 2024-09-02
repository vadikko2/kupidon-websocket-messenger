import typing

from infrastructure.brokers import redis
from infrastructure.database.persistent import mock
from service import messanger as messanger_service


async def get_messanger(account_id: typing.Text) -> messanger_service.Messanger:
    return messanger_service.Messanger(
        account_id,
        broker=redis.RedisMessageBroker('redis://localhost:6379'),
        uow=mock.MockMessageUoW()
    )
