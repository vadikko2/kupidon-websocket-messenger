import functools
import logging
import typing

import cqrs
import fastapi
from cqrs.container import di as di_container_impl
from cqrs.events import bootstrap as event_bootstrap
from cqrs.requests import bootstrap as request_bootstrap
from fastapi import status

from adapters.redis import connections
from infrastructure.brokers import messages_broker, redis
from infrastructure.storages import attachment_storage, s3
from presentation.api.schema import validators
from service import dependencies, mapping
from service.handlers.requests.subscriptions import subscription as subscription_service

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
    return redis.RedisMessageBroker(connections.RedisConnectionFactory())


def attachment_storage_factory() -> attachment_storage.AttachmentStorage:
    return s3.S3AttachmentStorage()


async def subscription_service_factory(
    broker: messages_broker.MessageBroker = fastapi.Depends(
        subscription_broker_factory,
    ),
) -> subscription_service.SubscriptionService:
    return subscription_service.SubscriptionService(broker=broker)


async def get_account_id(
    account_id: typing.Optional[typing.Text] = validators.AccountId(),
) -> typing.Text:
    """Returns account id from request header"""
    if account_id is None:
        logger.error("AccountID header not provided")
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="AccountID header not provided",
        )
    return account_id


async def get_account_id_ws(
    account_id: typing.Optional[typing.Text] = validators.AccountId(),
) -> typing.Text:
    """Returns account id from request header for WebSocket endpoints"""
    if account_id is None:
        logger.error("AccountID header not provided")
        raise fastapi.WebSocketException(
            code=status.HTTP_400_BAD_REQUEST,
            reason="AccountID header not provided",
        )
    return account_id
