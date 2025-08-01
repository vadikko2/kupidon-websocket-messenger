from cqrs import events, requests

from domain import events as domain_events
from service.handlers.events.chats import (
    new_chat as new_chat_handler,
    participants as participants_handler,
    tapping as tapping_handler,
)
from service.handlers.events.messages import (
    message_deleted as message_deleted_handler,
    message_read as message_reed_handler,
    message_updated as message_updated_handler,
    new_message_added as new_message_added_handler,
)
from service.handlers.events.reactions import (
    message_reacted as message_reacted_handler,
    message_unreacted as message_unreacted_handler,
)
from service.handlers.requests.attachments import (
    get_attachments as get_attachments_handler,
    upload_attachment as upload_attachment_handler,
    upload_circle as upload_circle_handler,
    upload_image as upload_image_handler,
    upload_voice as upload_voice_handler,
)
from service.handlers.requests.chats import (
    delete_chat as delete_chat_handler,
    get_chats as get_chats_handler,
    open_chat as open_chat_handler,
)
from service.handlers.requests.messages import (
    apply_message as apply_message_handler,
    delete_message as delete_message_handler,
    get_messages as get_messages_handler,
    send_message as send_message_handler,
    update_message as update_message_handler,
)
from service.handlers.requests.reactions import (
    get_reactors as get_reactors_handler,
    react_message as react_message_handler,
    unreact_message as unreact_message_handler,
)
from service.requests.attachments import (
    get_attachments as get_attachments_request,
    upload_attachment as upload_attachment_request,
    upload_circle as upload_circle_request,
    upload_image as upload_image_request,
    upload_voice as upload_voice_request,
)
from service.requests.chats import (
    delete_chat as delete_chat_request,
    get_chats as get_chats_request,
    open_chat as open_chat_request,
)
from service.requests.messages import (
    apply_message as apply_message_request,
    delete_message as delete_message_request,
    get_messages as get_messages_request,
    send_message as send_message_request,
    update_message as update_message_request,
)
from service.requests.reactions import (
    get_reactors as get_reactors_request,
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
    mapper.bind(delete_chat_request.DeleteChat, delete_chat_handler.DeleteChatHandler)
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
        update_message_request.UpdateMessage,
        update_message_handler.UpdateMessageHandler,
    )
    mapper.bind(
        get_messages_request.GetMessagePreview,
        get_messages_handler.GetMessagePreviewHandler,
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
        upload_voice_request.UploadVoice,
        upload_voice_handler.UploadVoiceHandler,
    )
    mapper.bind(
        upload_circle_request.UploadCircle,
        upload_circle_handler.UploadCircleHandler,
    )
    mapper.bind(
        upload_image_request.UploadImage,
        upload_image_handler.UploadImageHandler,
    )
    mapper.bind(
        react_message_request.ReactMessage,
        react_message_handler.ReactMessageHandler,
    )
    mapper.bind(
        unreact_message_request.UnreactMessage,
        unreact_message_handler.UnreactMessageHandler,
    )
    mapper.bind(
        get_reactors_request.GetReactors,
        get_reactors_handler.GetReactorsHandler,
    )


def init_events(mapper: events.EventMap) -> None:
    mapper.bind(
        domain_events.NewMessageAdded,
        new_message_added_handler.NewMessageAddedHandler,
    )
    mapper.bind(
        domain_events.MessageRead,
        message_reed_handler.MessageReadHandler,
    )
    mapper.bind(
        domain_events.MessageUpdated,
        message_updated_handler.MessageUpdatedHandler,
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
    mapper.bind(
        domain_events.TappingInChat,
        tapping_handler.TappingInChatHandler,
    )
    mapper.bind(
        domain_events.NewParticipantAdded,
        participants_handler.NewParticipantAddedHandler,
    )
    mapper.bind(
        domain_events.NewParticipantAdded,
        new_chat_handler.AddedIntoNewChatHandler,
    )
