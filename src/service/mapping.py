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
    upload_circle as upload_circle_handler,
    upload_image as upload_image_handler,
    upload_voice as upload_voice_handler,
)
from service.handlers.requests.chats import (
    add_tag as add_tag_handler,
    delete_chat as delete_chat_handler,
    get_chats as get_chats_handler,
    open_chat as open_chat_handler,
    remove_tag as remove_tag_handler,
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
from service.models.attachments import (
    get_attachments as get_attachments_model,
    upload_circle as upload_circle_model,
    upload_image as upload_image_model,
    upload_voice as upload_voice_model,
)
from service.models.chats import (
    add_tag as add_tag_model,
    delete_chat as delete_chat_model,
    get_chats as get_chats_model,
    open_chat as open_chat_model,
    remove_tag as remove_tag_model,
)
from service.models.messages import (
    apply_message as apply_message_model,
    delete_message as delete_message_model,
    get_messages as get_messages_model,
    send_message as send_message_model,
    update_message as update_message_model,
)
from service.models.reactions import (
    get_reactors as get_reactors_model,
    react_message as react_message_model,
    unreact_message as unreact_message_model,
)


def init_requests(mapper: requests.RequestMap) -> None:
    mapper.bind(
        apply_message_model.ApplyMessage,
        apply_message_handler.ApplyMessageHandler,
    )
    mapper.bind(
        delete_message_model.DeleteMessage,
        delete_message_handler.DeleteMessageHandler,
    )
    mapper.bind(open_chat_model.OpenChat, open_chat_handler.OpenChatHandler)
    mapper.bind(delete_chat_model.DeleteChat, delete_chat_handler.DeleteChatHandler)
    mapper.bind(add_tag_model.AddTag, add_tag_handler.AddTagHandler)
    mapper.bind(remove_tag_model.RemoveTag, remove_tag_handler.RemoveTagHandler)
    mapper.bind(
        send_message_model.SendMessage,
        send_message_handler.SendMessageHandler,
    )
    mapper.bind(get_chats_model.GetChats, get_chats_handler.GetChatsHandler)
    mapper.bind(
        get_messages_model.GetMessages,
        get_messages_handler.GetMessagesHandler,
    )
    mapper.bind(
        update_message_model.UpdateMessage,
        update_message_handler.UpdateMessageHandler,
    )
    mapper.bind(
        get_messages_model.GetMessagePreview,
        get_messages_handler.GetMessagePreviewHandler,
    )
    mapper.bind(
        get_attachments_model.GetAttachments,
        get_attachments_handler.GetAttachmentsHandler,
    )
    mapper.bind(
        upload_voice_model.UploadVoice,
        upload_voice_handler.UploadVoiceHandler,
    )
    mapper.bind(
        upload_circle_model.UploadCircle,
        upload_circle_handler.UploadCircleHandler,
    )
    mapper.bind(
        upload_image_model.UploadImage,
        upload_image_handler.UploadImageHandler,
    )
    mapper.bind(
        react_message_model.ReactMessage,
        react_message_handler.ReactMessageHandler,
    )
    mapper.bind(
        unreact_message_model.UnreactMessage,
        unreact_message_handler.UnreactMessageHandler,
    )
    mapper.bind(
        get_reactors_model.GetReactors,
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
