from domain import events
import cqrs


class MessageReedHandler(cqrs.EventHandler[events.MessageRead]):
    pass
