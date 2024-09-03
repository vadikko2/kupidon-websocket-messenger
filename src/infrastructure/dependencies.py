import functools

import di
from di import dependent

from infrastructure.brokers import protocol as broker_protocol, redis
from service import unit_of_work

container = di.Container()

UoWBind = di.bind_by_type(
    dependent.Dependent(unit_of_work.MockMessageUoW, scope="request"),
    unit_of_work.UoW,
)
BrokerBind = di.bind_by_type(
    dependent.Dependent(
        functools.partial(redis.RedisMessageBroker, "redis://localhost:6379"),
        scope="request",
    ),
    broker_protocol.MessageBroker,
)

container.bind(UoWBind)
container.bind(BrokerBind)
