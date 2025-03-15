import redis.asyncio as redis

from adapters.redis import pools


class RedisConnectionFactory:
    def __call__(self) -> redis.Redis:
        return redis.Redis(connection_pool=pools.connection_pool)
