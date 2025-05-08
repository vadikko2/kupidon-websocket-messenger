import asyncio
import logging

import orjson
import socketio
from socketio import async_redis_manager

from infrastructure.brokers import redis as redis_broker
from infrastructure.database.cache.redis import connections, settings as redis_settings
from service.handlers.requests.subscriptions import subscription as subscription_service

logger = logging.getLogger(__name__)

# TODO Это отвратительно. Необходимо переписать весь файл
sio = socketio.AsyncServer(
    async_mode="asgi",
    client_manager=async_redis_manager.AsyncRedisManager(
        redis_settings.redis_settings.dsn(),
    ),
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True,
)


async def subscription_handler(
    sid: str,
    account_id: str,
):
    try:
        async with connections.RedisConnectionFactory()() as redis:
            await redis.hset(  # pyright: ignore[reportGeneralTypeIssues]
                f"socketio:session:{sid}",
                mapping={
                    "account_id": account_id,
                    "connected": "1",
                },
            )
            await redis.expire(f"socketio:session:{sid}", 3600)
            subscription = subscription_service.SubscriptionService(
                redis_broker.RedisMessageBroker(lambda: redis),
            )
            async with subscription.start_subscription(account_id) as subscription:
                while True:
                    connected = await redis.hexists(  # pyright: ignore[reportGeneralTypeIssues]
                        f"socketio:session:{sid}",
                        "connected",
                    )
                    if not connected:
                        break

                    try:
                        message = await subscription.wait_events()
                        if message is None:
                            await asyncio.sleep(0.05)
                            continue

                        json_message = orjson.loads(message)
                        await sio.emit(
                            json_message.get("event_name"),
                            json_message,
                            to=sid,
                        )
                        logger.debug(f"{account_id} got message {json_message}")
                    except Exception as e:
                        logger.error(f"Error in subscription handler: {e}")
                        break
    except Exception as e:
        logger.error(f"Subscription error: {e}")
    finally:
        await sio.disconnect(sid)


@sio.on("connect", namespace="/v2/subscriptions")  # pyright: ignore[reportOptionalCall]
async def connect(sid, environ):
    logger.debug(f"Connection attempt from {environ.get('PATH_INFO')}")
    logger.debug(f"Query string: {environ.get('QUERY_STRING')}")
    logger.debug(f"Headers: {environ.get('HTTP_HEADERS')}")

    try:
        account_id = "account-id"
        sio.start_background_task(
            subscription_handler,
            sid,
            account_id,
        )
    except Exception as e:  # TODO заменить на обработку ошибки авторизации
        logger.error(f"Error in handle_connect: {e}")
        return False
    else:
        logger.debug(f"Socket.IO connected to {account_id}")
        return True


@sio.on("disconnect", namespace="/v2/subscriptions")  # pyright: ignore[reportOptionalCall]
async def disconnect(sid: str):
    async with connections.RedisConnectionFactory()() as redis:
        account_id = await redis.hget(
            f"socketio:session:{sid}",  # pyright: ignore[reportGeneralTypeIssues]
            "account_id",
        )
        await redis.hdel(f"socketio:session:{sid}", "connected")  # pyright: ignore[reportGeneralTypeIssues]
        await redis.expire(f"socketio:session:{sid}", 60)  # pyright: ignore[reportGeneralTypeIssues]

    logger.debug(f"Socket.IO disconnected from {account_id}")
