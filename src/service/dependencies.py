import functools
import typing

import di
from di import dependent

from domain import attachments
from infrastructure.brokers import messages_broker, redis
from infrastructure.helpers.attachments.preprocessors import chain, jpeg_preprocessors
from infrastructure.settings import redis_settings
from infrastructure.storages import attachment_storage, s3
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
container.bind(PreprocessingChainBind)
container.bind(AttachmentStorageBind)
