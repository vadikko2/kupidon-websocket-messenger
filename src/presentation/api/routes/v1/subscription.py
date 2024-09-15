import asyncio
import logging
import typing

import fastapi
import orjson
from fastapi import status

from presentation import dependencies
from service.services import subscription as subscription_service

router = fastapi.APIRouter(
    prefix="/subscriptions",
    tags=["Incoming messages subscription"],
)

logger = logging.getLogger(__name__)


@router.websocket("")
async def websocket_endpoint(
    websocket: fastapi.WebSocket,
    account_id: typing.Text = fastapi.Depends(dependencies.get_account_id_ws),
    subscription: subscription_service.SubscriptionService = fastapi.Depends(
        dependency=dependencies.subscription_service_factory,
    ),
):
    """
    # Returns all events for the specified account
    """
    await websocket.accept()
    logger.debug(f"Websocket connected to {account_id}")
    async with subscription.start_subscription(account_id):
        try:
            while True:
                try:
                    message = await subscription.wait_events()
                    if message is None:
                        await asyncio.sleep(0.05)
                        continue
                    logger.debug(f"{account_id} got message {message}")
                    await websocket.send_json(orjson.loads(message))
                except (fastapi.WebSocketDisconnect, fastapi.WebSocketException):
                    logger.debug(f"Websocket disconnected from {account_id}")
                    return
                except Exception as e:
                    logger.error(f"Error in websocket endpoint: {e}")
                    continue
        finally:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
            logger.debug(f"Websocket disconnected from {account_id}")
