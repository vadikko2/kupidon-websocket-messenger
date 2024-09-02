import asyncio
import logging
import typing
import uuid

import fastapi
from starlette import status

from presentation.api.dependencies import messangers
from service import messanger as messanger_service

router = fastapi.APIRouter(prefix="/incoming-messages", tags=["Incoming messages"])

logger = logging.getLogger(__name__)


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: fastapi.WebSocket,
    account_id: typing.Optional[typing.Text] = fastapi.Header(
        None,
        description="Target account ID",
        alias="UserID",
        example="account-id",
    ),
    messanger: messanger_service.Messanger = fastapi.Depends(
        dependency=messangers.get_messanger,
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


@router.put("/{message_id}/receive", status_code=status.HTTP_204_NO_CONTENT)
async def apply_message_receive(
    message_id: uuid.UUID,
    account_id: typing.Optional[typing.Text] = fastapi.Header(
        None,
        description="Target account ID",
        alias="UserID",
        example="account-id",
    ),
    messanger: messanger_service.Messanger = fastapi.Depends(
        dependency=messangers.get_messanger,
    ),
) -> fastapi.Response:
    """
    # Apply message as received
    """
    if account_id is None:
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="UserID header not provided",
        )

    await messanger.mark_as_read(account_id, message_id)
    return fastapi.Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{message_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def apply_message_read(
    message_id: uuid.UUID,
    account_id: typing.Optional[typing.Text] = fastapi.Header(
        None,
        description="Target account ID",
        alias="UserID",
        example="account-id",
    ),
    messanger: messanger_service.Messanger = fastapi.Depends(
        dependency=messangers.get_messanger,
    ),
) -> fastapi.Response:
    """
    # Apply message as read
    """
    if account_id is None:
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="UserID header not provided",
        )

    await messanger.mark_as_read(account_id, message_id)
    return fastapi.Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{message_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: uuid.UUID,
    account_id: typing.Optional[typing.Text] = fastapi.Header(
        None,
        description="Target account ID",
        alias="UserID",
        example="account-id",
    ),
    messanger: messanger_service.Messanger = fastapi.Depends(
        dependency=messangers.get_messanger,
    ),
) -> fastapi.Response:
    """
    # Apply message as read
    """
    if account_id is None:
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="UserID header not provided",
        )

    await messanger.delete_message(account_id, message_id)
    return fastapi.Response(status_code=status.HTTP_204_NO_CONTENT)
