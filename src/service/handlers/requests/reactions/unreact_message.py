import cqrs

from domain import messages
from service import exceptions, unit_of_work
from service.requests.reactions import unreact_message


class UnreactMessageHandler(cqrs.RequestHandler[unreact_message.UnreactMessage, None]):
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow

    @property
    def events(self):
        return self.uow.get_events()

    async def handle(self, request: unreact_message.UnreactMessage) -> None:
        async with self.uow:
            message = await self.uow.message_repository.get(request.message_id)

            if message is None or message.status == messages.MessageStatus.DELETED:
                raise exceptions.MessageNotFound(request.message_id)

            reaction = next(
                filter(
                    lambda r: r.emoji == request.reaction,
                    message.reactions,
                ),
                None,
            )
            if reaction is None:
                raise exceptions.ReactionNotFound(request.reaction)

            message.unreact(reaction)

            await self.uow.message_repository.update(message)
            await self.uow.commit()
