import functools

import di
from di import dependent

from infrastructure.brokers import messages_broker, redis
from infrastructure.settings import redis_settings
from service import unit_of_work

container = di.Container()

UoWBind = di.bind_by_type(
    dependent.Dependent(unit_of_work.MockMessageUoW, scope="request"),
    unit_of_work.UoW,
)
BrokerBind = di.bind_by_type(
    dependent.Dependent(
        functools.partial(redis.RedisMessageBroker, redis_settings.dsn()),
        scope="request",
    ),
    messages_broker.MessageBroker,
)

container.bind(UoWBind)
container.bind(BrokerBind)
