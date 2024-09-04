import asyncio
import logging
import typing

import fastapi
from starlette import status

from presentation import dependencies
from service import subscription_service as messanger_service

router = fastapi.APIRouter(
    prefix="/subscriptions",
    tags=["Incoming messages subscription"],
)

logger = logging.getLogger(__name__)


@router.websocket("")
async def websocket_endpoint(
    websocket: fastapi.WebSocket,
    account_id: typing.Optional[typing.Text] = fastapi.Header(
        None,
        description="Target account ID",
        alias="UserID",
        example="account-id",
    ),
    messanger: messanger_service.SubscriptionService = fastapi.Depends(
        dependency=dependencies.get_subscription_service,
    ),
):
    """
    # Returns all incoming messages for the specified account
    """
    if account_id is None:
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="UserID header not provided",
        )

    await websocket.accept()
    logger.debug(f"Websocket connected to {account_id}")
    async with messanger.start_subscription(account_id):
        try:
            while True:
                message = await messanger.wait_message()
                if message is None:
                    await asyncio.sleep(0.05)
                    continue
                logger.debug(f"{account_id} got message {message.message_id}")
                await websocket.send_json(message.model_dump(mode="json"))
        except (fastapi.WebSocketDisconnect, fastapi.WebSocketException):
            logger.debug(f"Websocket disconnected from {account_id}")
            return
