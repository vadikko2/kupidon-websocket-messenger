import cqrs

from service import exceptions, unit_of_work
from service.requests.reactions import get_reactors as get_reactors_request
from service.validators import messages as message_validators


class GetReactorsHandler(
    cqrs.RequestHandler[
        get_reactors_request.GetReactors,
        get_reactors_request.Reactors,
    ],
):
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow

    @property
    def events(self):
        return []

    async def handle(
        self,
        request: get_reactors_request.GetReactors,
    ) -> get_reactors_request.Reactors:
        async with self.uow:
            message = await self.uow.message_repository.get(request.message_id)
            if not message:
                raise exceptions.MessageNotFound(request.message_id)
            message_validators.raise_if_message_deleted(message)

        reactors = []
        for reaction in message.reactions:
            if reaction.emoji == request.emoji:
                reactors.append(reaction.reactor)

        return get_reactors_request.Reactors(reactors=reactors)
