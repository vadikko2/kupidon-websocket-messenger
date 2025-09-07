import functools
import logging

import cqrs
import fastapi
from cqrs.container import di as di_container_impl
from cqrs.events import bootstrap as event_bootstrap
from cqrs.requests import bootstrap as request_bootstrap

from infrastructure import dependencies
from infrastructure.brokers import messages_broker, redis as redis_broker
from infrastructure.database.cache.redis import connections
from infrastructure.storages import s3
from service import mapping
from service.handlers.requests.subscriptions import subscription as subscription_service
from service.interfaces import attachment_storage

logger = logging.getLogger(__name__)


@functools.lru_cache
def request_mediator_factory() -> cqrs.RequestMediator:
    return request_bootstrap.bootstrap(
        di_container=dependencies.container,
        commands_mapper=mapping.init_requests,
        domain_events_mapper=mapping.init_events,
    )


@functools.lru_cache
def event_mediator_factor() -> cqrs.EventMediator:
    return event_bootstrap.bootstrap(
        di_container=dependencies.container,
        events_mapper=mapping.init_events,
    )


@functools.lru_cache
def event_emitter_factory() -> cqrs.EventEmitter:
    container = di_container_impl.DIContainer()
    container.attach_external_container(dependencies.container)
    return request_bootstrap.setup_event_emitter(
        container=container,
        domain_events_mapper=mapping.init_events,
    )


def subscription_broker_factory() -> messages_broker.MessageBroker:
    return redis_broker.RedisMessageBroker(connections.RedisConnectionFactory())


def attachment_storage_factory() -> attachment_storage.AttachmentStorage:
    return s3.S3AttachmentStorage()


async def subscription_service_factory(
    broker: messages_broker.MessageBroker = fastapi.Depends(
        subscription_broker_factory,
    ),
) -> subscription_service.SubscriptionService:
    return subscription_service.SubscriptionService(broker=broker)
