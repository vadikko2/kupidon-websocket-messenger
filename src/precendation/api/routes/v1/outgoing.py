import typing

import fastapi
from fastapi import status

from domain import message as message_entity
from precendation.api.dependencies import messangers
from precendation.api.schema import validators
from service import messanger as messanger_service

router = fastapi.APIRouter(prefix='/outgoing-messages')


@router.post('/{receiver}', status_code=status.HTTP_201_CREATED)
async def send_message(
        receiver: typing.Text,
        account_id: typing.Optional[typing.Text] = fastapi.Header(
            None,
            description="Target account ID",
            alias="UserID",
            example="account-id",
        ),
        content: typing.Text = validators.MessageBody(),
        messanger: messanger_service.Messanger = fastapi.Depends(dependency=messangers.get_messanger),
):
    """
    # Send message to receiver
    """
    message = message_entity.Message(sender=account_id, receiver=receiver, content=content)
    await messanger.send_message(message)

    return fastapi.Response(status_code=status.HTTP_201_CREATED)
