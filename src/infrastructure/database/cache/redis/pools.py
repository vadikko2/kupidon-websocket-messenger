import redis.asyncio as redis

from infrastructure.database.cache.redis import settings

connection_pool = redis.ConnectionPool.from_url(
    settings.redis_settings.dsn(),
    decode_responses=True,
)
