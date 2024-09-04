from cqrs import events, requests

from domain import events as domain_events
from service.handlers import (
    apply_message as apply_message_handler,
    delete_message as delete_message_handler,
    get_chats as get_chats_handler,
    get_messages as get_history_handler,
    new_message_added as new_message_added_handler,
    open_chat as open_chat_handler,
    send_message as send_message_handler,
)
from service.requests import (
    apply_message as apply_message_request,
    delete_message as delete_message_request,
    get_chats as get_chats_request,
    get_messages as get_history_request,
    open_chat as open_chat_request,
    send_message as send_message_request,
)


def init_requests(mapper: requests.RequestMap) -> None:
    mapper.bind(
        apply_message_request.ApplyMessageRead,
        apply_message_handler.ApplyMessageReadHandler,
    )
    mapper.bind(
        apply_message_request.ApplyMessageReceive,
        apply_message_handler.ApplyMessageReceiveHandler,
    )
    mapper.bind(
        delete_message_request.DeleteMessage,
        delete_message_handler.DeleteMessageHandler,
    )
    mapper.bind(open_chat_request.OpenChat, open_chat_handler.OpenChatHandler)
    mapper.bind(
        send_message_request.SendMessage,
        send_message_handler.SendMessageHandler,
    )
    mapper.bind(get_chats_request.GetChats, get_chats_handler.GetChatsHandler)
    mapper.bind(get_history_request.GetMessages, get_history_handler.GetMessagesHandler)


def init_events(mapper: events.EventMap) -> None:
    mapper.bind(
        domain_events.NewMessageAdded,
        new_message_added_handler.NewMessageAddedHandler,
    )
