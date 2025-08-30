import cqrs

from service import exceptions
from service.interfaces import unit_of_work
from service.models.reactions import unreact_message
from service.validators import messages as message_validators


class UnreactMessageHandler(cqrs.RequestHandler[unreact_message.UnreactMessage, None]):
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow

    @property
    def events(self):
        return list(self.uow.get_events())

    async def handle(self, request: unreact_message.UnreactMessage) -> None:
        async with self.uow:
            message = await self.uow.message_repository.get(request.message_id)
            if not message:
                raise exceptions.MessageNotFound(request.message_id)
            message_validators.raise_if_message_deleted(message)

            reaction = next(
                filter(
                    lambda r: r.emoji == request.reaction,
                    message.reactions,
                ),
                None,
            )
            if reaction is None:
                return

            message.unreact(reaction)

            await self.uow.message_repository.update(message)
            await self.uow.commit()
