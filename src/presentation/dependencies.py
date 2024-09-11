import functools

from cqrs.requests.bootstrap import bootstrap

from infrastructure import dependencies
from infrastructure.brokers import redis
from infrastructure.settings import redis_settings
from service import mapping, subscription_service, unit_of_work


@functools.lru_cache
def get_request_mediator():
    return bootstrap(
        di_container=dependencies.container,
        commands_mapper=mapping.init_requests,
        domain_events_mapper=mapping.init_events,
    )


async def get_subscription_service() -> subscription_service.SubscriptionService:
    return subscription_service.SubscriptionService(
        broker=redis.RedisMessageBroker(redis_settings.dsn()),
        uow=unit_of_work.MockMessageUoW(),
    )
