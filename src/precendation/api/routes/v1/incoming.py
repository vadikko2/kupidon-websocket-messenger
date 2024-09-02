import logging
import typing

import fastapi
import orjson

from precendation.api.dependencies import messangers
from service import messanger as messanger_service

router = fastapi.APIRouter(prefix='/incoming-messages')

logger = logging.getLogger(__name__)


@router.websocket('/{account_id}')
async def websocket_endpoint(
    websocket: fastapi.WebSocket,
    account_id: typing.Text,
    messanger: messanger_service.Messanger = fastapi.Depends(dependency=messangers.get_messanger),
):
    """
    # Returns all incoming messages for the specified account
    """
    await websocket.accept()
    logger.debug(f"Websocket connected to {account_id}")
    async with messanger:
        try:
            while True:
                message = await messanger.get_message()
                if message is None:
                    continue
                logger.debug(f"{account_id} got message {message.message_id}")
                await websocket.send_json(orjson.dumps(message.model_dump(mode="json")))
        except fastapi.WebSocketDisconnect:
            logger.debug(f"Websocket disconnected from {account_id}")
            return
