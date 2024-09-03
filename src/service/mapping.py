from cqrs import requests

from service.commands import (
    apply_message as apply_message_command,
    delete_message as delete_message_command,
    open_chat as open_chat_command,
    send_message as send_message_command,
)
from service.handlers import (
    apply_message as apply_message_handler,
    delete_message as delete_message_handler,
    get_chats as get_chats_handler,
    get_history as get_history_handler,
    open_chat as open_chat_handler,
    send_message as send_message_handler,
)
from service.queries import (
    get_chats as get_chats_query,
    get_history as get_history_query,
)


def init_commands(mapper: requests.RequestMap) -> None:
    mapper.bind(
        apply_message_command.ApplyMessageRead,
        apply_message_handler.ApplyMessageReadHandler,
    )
    mapper.bind(
        apply_message_command.ApplyMessageReceive,
        apply_message_handler.ApplyMessageReceiveHandler,
    )
    mapper.bind(
        delete_message_command.DeleteMessage,
        delete_message_handler.DeleteMessageHandler,
    )
    mapper.bind(open_chat_command.OpenChat, open_chat_handler.OpenChatHandler)
    mapper.bind(
        send_message_command.SendMessage,
        send_message_handler.SendMessageHandler,
    )


def init_queries(mapper: requests.RequestMap) -> None:
    mapper.bind(get_chats_query.GetChats, get_chats_handler.GetChatsHandler)
    mapper.bind(get_history_query.GetHistory, get_history_handler.GetHistoryHandler)
