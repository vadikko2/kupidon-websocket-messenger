import functools
import logging

import fastapi
from fastapi import responses

from infrastructure.brokers import redis
from presentation.api import dependencies
from presentation.api.schema import heathcheck as healthcheck_response

logger = logging.getLogger(__name__)

router = fastapi.APIRouter(tags=["Healthcheck"])


@router.get(
    "/",
    status_code=fastapi.status.HTTP_200_OK,
    response_model=healthcheck_response.Healthcheck,
    responses={
        fastapi.status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "Service Unavailable",
        },
        fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal Server Error",
        },
    },
)
async def healthcheck(
    redis_broker: redis.RedisMessageBroker = fastapi.Depends(
        dependencies.subscription_broker_factory,
    ),
):
    """
    # Health checks
    """
    checks = {
        "redis": functools.partial(redis_broker.connect.ping),
        # TODO add other checks
    }
    check_results = []
    healthy = True
    for name, check in checks.items():
        try:
            await check()
            check_results.append(healthcheck_response.Check(name=name, healthy=True))
        except Exception as error:
            healthy = False
            check_results.append(
                healthcheck_response.Check(name=name, healthy=False, error=str(error)),
            )
            logger.error(f"{name} is unhealthy: {error}")

    status_code = (
        fastapi.status.HTTP_200_OK
        if healthy
        else fastapi.status.HTTP_503_SERVICE_UNAVAILABLE
    )

    return responses.JSONResponse(
        status_code=status_code,
        content=healthcheck_response.Healthcheck(
            checks=check_results,
        ).model_dump_json(),
    )
