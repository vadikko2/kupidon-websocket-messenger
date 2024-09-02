import logging
import typing
import uuid

import fastapi
import orjson
from starlette import status

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
                message = await messanger.wait_message()
                if message is None:
                    continue
                logger.debug(f"{account_id} got message {message.message_id}")
                await websocket.send_json(orjson.dumps(message.model_dump(mode="json")))
        except fastapi.WebSocketDisconnect:
            logger.debug(f"Websocket disconnected from {account_id}")
            return


@router.put('/{message_id}/receive', status_code=status.HTTP_204_NO_CONTENT)
async def apply_message_read(
        message_id: uuid.UUID,
        account_id: typing.Optional[typing.Text] = fastapi.Header(
            None,
            description="Target account ID",
            alias="UserID",
            example="account-id",
        ),
        messanger: messanger_service.Messanger = fastapi.Depends(dependency=messangers.get_messanger)
) -> fastapi.Response:
    """
    # Apply message as received
    """
    await messanger.mark_as_read(account_id, message_id)
    return fastapi.Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put('/{message_id}/read', status_code=status.HTTP_204_NO_CONTENT)
async def apply_message_read(
        message_id: uuid.UUID,
        account_id: typing.Optional[typing.Text] = fastapi.Header(
            None,
            description="Target account ID",
            alias="UserID",
            example="account-id",
        ),
        messanger: messanger_service.Messanger = fastapi.Depends(dependency=messangers.get_messanger)
) -> fastapi.Response:
    """
    # Apply message as read
    """
    await messanger.mark_as_read(account_id, message_id)
    return fastapi.Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put('/{message_id}/delete', status_code=status.HTTP_204_NO_CONTENT)
async def apply_message_read(
        message_id: uuid.UUID,
        account_id: typing.Optional[typing.Text] = fastapi.Header(
            None,
            description="Target account ID",
            alias="UserID",
            example="account-id",
        ),
        messanger: messanger_service.Messanger = fastapi.Depends(dependency=messangers.get_messanger)
) -> fastapi.Response:
    """
    # Apply message as read
    """
    await messanger.delete_message(account_id, message_id)
    return fastapi.Response(status_code=status.HTTP_204_NO_CONTENT)
