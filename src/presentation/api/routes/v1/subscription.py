import asyncio
import logging
import typing

import cqrs
import fastapi

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
    account_id: typing.Text = fastapi.Depends(dependencies.get_account_id),
    messanger: subscription_service.SubscriptionService = fastapi.Depends(
        dependency=dependencies.get_subscription_service,
    ),
    emitter: cqrs.EventEmitter = fastapi.Depends(
        dependency=dependencies.get_event_emitter,
    ),
):
    """
    # Returns all incoming messages for the specified account
    """
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

                for event in messanger.events():
                    try:
                        await emitter.emit(event)
                    except Exception as emit_error:
                        logger.error(f"Failed to emit event {event}: {emit_error}")
        except (fastapi.WebSocketDisconnect, fastapi.WebSocketException):
            logger.debug(f"Websocket disconnected from {account_id}")
            return
