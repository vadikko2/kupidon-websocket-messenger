import typing

import fastapi
from fastapi import status

from domain import message as message_entity
from presentation.api.dependencies import messangers
from presentation.api.schema import requests, responses, validators
from service import messanger as messanger_service

router = fastapi.APIRouter(prefix="/outgoing-messages", tags=["Outgoing messages"])


@router.post("/{receiver}", status_code=status.HTTP_201_CREATED)
async def send_message(
    receiver: typing.Text,
    account_id: typing.Optional[typing.Text] = fastapi.Header(
        None,
        description="Target account ID",
        alias="UserID",
        example="account-id",
    ),
    content: typing.Text = validators.MessageBody(),
    attachments: typing.List[requests.Attachment] = fastapi.Body(default_factory=list),
    messanger: messanger_service.Messanger = fastapi.Depends(
        dependency=messangers.get_messanger,
    ),
) -> responses.MessageSent:
    """
    # Send message to receiver
    """
    if account_id is None:
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="UserID header not provided",
        )

    message = message_entity.Message(
        sender=account_id,
        receiver=receiver,
        content=content,
        attachments=[
            message_entity.Attachment(
                url=attachment.url,
                name=attachment.name,
                content_type=attachment.content_type,
            )
            for attachment in attachments
        ],
    )
    await messanger.send_message(message)

    return responses.MessageSent(
        message_id=message.message_id,
        receiver=receiver,
        timestamp=message.created,
    )
