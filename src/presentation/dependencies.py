import functools
import typing

import fastapi
from cqrs.container import di as di_container_impl
from cqrs.requests.bootstrap import bootstrap, setup_event_emitter
from fastapi import status

from infrastructure import dependencies
from infrastructure.brokers import redis
from infrastructure.settings import redis_settings
from infrastructure.storages import mock
from presentation.api.schema import validators
from service import mapping, unit_of_work
from service.services import (
    subscription as subscription_service,
    upload_attachment as upload_attachment_service,
)


@functools.lru_cache
def get_request_mediator():
    return bootstrap(
        di_container=dependencies.container,
        commands_mapper=mapping.init_requests,
        domain_events_mapper=mapping.init_events,
    )


@functools.lru_cache
def get_event_emitter():
    container = di_container_impl.DIContainer()
    container.attach_external_container(dependencies.container)
    return setup_event_emitter(
        container=container,
        domain_events_mapper=mapping.init_events,
    )


async def get_subscription_service() -> subscription_service.SubscriptionService:
    return subscription_service.SubscriptionService(
        broker=redis.RedisMessageBroker(redis_settings.dsn()),
        uow=unit_of_work.MockMessageUoW(),
    )


async def get_upload_attachment_service() -> (
    upload_attachment_service.UploadAttachmentService
):
    return upload_attachment_service.UploadAttachmentService(
        storage=mock.MockAttachmentStorage(),
        uow=unit_of_work.MockMessageUoW(),
    )


async def get_account_id(
    account_id: typing.Optional[typing.Text] = validators.AccountId(),
) -> typing.Text:
    """Returns account id from request header"""
    if account_id is None:
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="AccountID header not provided",
        )
    return account_id
