import functools
import typing

import di
import redis.asyncio as redis
from di import dependent

from domain import attachments
from infrastructure import unit_of_work as mock_unit_of_work
from infrastructure.brokers import messages_broker, redis as redis_broker
from infrastructure.database.cache.redis import connections as redis_connections
from infrastructure.helpers.attachments.preprocessors import chain, jpeg_preprocessors
from infrastructure.storages import s3
from service import unit_of_work
from service.interfaces import attachment_storage

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
Chains: typing.TypeAlias = typing.List[chain.PreprocessingChain]

PreprocessingChainBind = di.bind_by_type(
    dependent.Dependent(
        functools.partial(
            lambda: [
                chain.PreprocessingChain(
                    content_type=attachments.AttachmentType.IMAGE,
                    chain_name="image",
                    preprocessors=[
                        jpeg_preprocessors.JpegTranscodeAttachmentPreprocessor(),
                        jpeg_preprocessors.JPEGPreview200x200AttachmentPreprocessor(),
                        jpeg_preprocessors.JPEGPreview100x100AttachmentPreprocessor(),
                    ],
                ),
            ],
        ),
        scope="request",
    ),
    Chains,
)
AttachmentStorageBind = di.bind_by_type(
    dependent.Dependent(s3.S3AttachmentStorage, scope="request"),
    attachment_storage.AttachmentStorage,
)

container.bind(UoWBind)
container.bind(BrokerBind)
container.bind(RedisBind)
container.bind(PreprocessingChainBind)
container.bind(AttachmentStorageBind)
