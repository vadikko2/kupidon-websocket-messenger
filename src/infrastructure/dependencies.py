import typing

import di
import redis.asyncio as redis
from di import dependent

from infrastructure import unit_of_work as mock_unit_of_work
from infrastructure.brokers import messages_broker, redis as redis_broker
from infrastructure.database.cache.redis import connections as redis_connections
from infrastructure.services import iam_service
from infrastructure.storages import s3
from service.interfaces import attachment_storage, unit_of_work
from service.interfaces.services import iam_service as iam_service_interface

container = di.Container()

UoWBind = di.bind_by_type(
    dependent.Dependent(mock_unit_of_work.MockMessageUoW, scope="request"),
    unit_of_work.UoW,
)
BrokerBind = di.bind_by_type(
    dependent.Dependent(
        redis_broker.RedisMessageBroker,
        scope="request",
    ),
    messages_broker.MessageBroker,
)
RedisBind = di.bind_by_type(
    dependent.Dependent(redis_connections.RedisConnectionFactory, scope="request"),
    typing.Callable[[], redis.Redis],  # pyright: ignore[reportArgumentType]
)

AttachmentStorageBind = di.bind_by_type(
    dependent.Dependent(s3.S3AttachmentStorage, scope="request"),
    attachment_storage.AttachmentStorage,
)

container.bind(
    di.bind_by_type(
        dependent.Dependent(
            iam_service.HttpIAMService,
            scope="request",
        ),
        iam_service_interface.IAMService,
    ),
)

container.bind(UoWBind)
container.bind(BrokerBind)
container.bind(RedisBind)
container.bind(AttachmentStorageBind)
