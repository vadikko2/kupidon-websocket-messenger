from cqrs import events, requests

from domain import events as domain_events
from service.handlers.attachments import (
    get_attachments as get_attachments_handler,
    upload_attachment as upload_attachment_handler,
)
from service.handlers.chats import (
    get_chats as get_chats_handler,
    open_chat as open_chat_handler,
)
from service.handlers.messages import (
    apply_message as apply_message_handler,
    delete_message as delete_message_handler,
    get_messages as get_messages_handler,
    message_deleted as message_deleted_handler,
    new_message_added as new_message_added_handler,
    send_message as send_message_handler,
)
from service.handlers.reactions import (
    message_reacted as message_reacted_handler,
    message_unreacted as message_unreacted_handler,
    react_message as react_message_handler,
    unreact_message as unreact_message_handler,
)
from service.requests.attachments import (
    get_attachments as get_attachments_request,
    upload_attachment as upload_attachment_request,
)
from service.requests.chats import (
    get_chats as get_chats_request,
    open_chat as open_chat_request,
)
from service.requests.messages import (
    apply_message as apply_message_request,
    delete_message as delete_message_request,
    get_messages as get_messages_request,
    send_message as send_message_request,
)
from service.requests.reactions import (
    react_message as react_message_request,
    unreact_message as unreact_message_request,
)


def init_requests(mapper: requests.RequestMap) -> None:
    mapper.bind(
        apply_message_request.ApplyMessage,
        apply_message_handler.ApplyMessageHandler,
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
    mapper.bind(
        get_messages_request.GetMessages,
        get_messages_handler.GetMessagesHandler,
    )
    mapper.bind(
        get_attachments_request.GetAttachments,
        get_attachments_handler.GetAttachmentsHandler,
    )
    mapper.bind(
        upload_attachment_request.UploadAttachment,
        upload_attachment_handler.UploadAttachmentHandler,
    )
    mapper.bind(
        react_message_request.ReactMessage,
        react_message_handler.ReactMessageHandler,
    )
    mapper.bind(
        unreact_message_request.UnreactMessage,
        unreact_message_handler.UnreactMessageHandler,
    )


def init_events(mapper: events.EventMap) -> None:
    mapper.bind(
        domain_events.NewMessageAdded,
        new_message_added_handler.NewMessageAddedHandler,
    )
    mapper.bind(
        domain_events.MessageReacted,
        message_reacted_handler.MessageReactedHandler,
    )
    mapper.bind(
        domain_events.MessageUnreacted,
        message_unreacted_handler.MessageUnreactedHandler,
    )
    mapper.bind(
        domain_events.MessageDeleted,
        message_deleted_handler.MessageDeletedHandler,
    )
