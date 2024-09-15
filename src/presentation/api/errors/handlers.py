from fastapi import status
from fastapi_app.exception_handlers import bind_exception, models
from starlette import requests

from domain import exceptions as domain_exceptions
from presentation.api.schema.requests import EmojiValidationError
from service import exceptions as service_exceptions


@bind_exception(status.HTTP_403_FORBIDDEN)
def change_status_access_donated_handler(
    _: requests.Request,
    error: service_exceptions.ChangeStatusAccessDonated,
) -> models.ErrorResponse:
    return models.ErrorResponse(message=str(error))


@bind_exception(status.HTTP_404_NOT_FOUND)
def message_not_found_handler(
    _: requests.Request,
    error: service_exceptions.MessageNotFound,
) -> models.ErrorResponse:
    return models.ErrorResponse(message=str(error))


@bind_exception(status.HTTP_404_NOT_FOUND)
def reaction_not_found_handler(
    _: requests.Request,
    error: service_exceptions.ReactionNotFound,
) -> models.ErrorResponse:
    return models.ErrorResponse(message=str(error))


@bind_exception(status.HTTP_404_NOT_FOUND)
def chat_not_found_handler(
    _: requests.Request,
    error: service_exceptions.ChatNotFound,
) -> models.ErrorResponse:
    return models.ErrorResponse(message=str(error))


@bind_exception(status.HTTP_400_BAD_REQUEST)
def message_not_for_chat_handler(
    _: requests.Request,
    error: service_exceptions.MessageNotForChat,
) -> models.ErrorResponse:
    return models.ErrorResponse(message=str(error))


@bind_exception(status.HTTP_404_NOT_FOUND)
def attachment_not_found_handler(
    _: requests.Request,
    error: service_exceptions.AttachmentNotFound,
) -> models.ErrorResponse:
    return models.ErrorResponse(message=str(error))


@bind_exception(status.HTTP_400_BAD_REQUEST)
def attachment_not_for_chat_handler(
    _: requests.Request,
    error: service_exceptions.AttachmentNotForChat,
) -> models.ErrorResponse:
    return models.ErrorResponse(message=str(error))


@bind_exception(status.HTTP_400_BAD_REQUEST)
def attachment_not_for_sender_handler(
    _: requests.Request,
    error: service_exceptions.AttachmentNotForSender,
) -> models.ErrorResponse:
    return models.ErrorResponse(message=str(error))


@bind_exception(status.HTTP_403_FORBIDDEN)
def not_participant_in_chat_handler(
    _: requests.Request,
    error: service_exceptions.ParticipantNotInChat,
) -> models.ErrorResponse:
    return models.ErrorResponse(message=str(error))


@bind_exception(status.HTTP_500_INTERNAL_SERVER_ERROR)
def start_subscription_error_handler(
    _: requests.Request,
    error: service_exceptions.StartSubscriptionError,
) -> models.ErrorResponse:
    return models.ErrorResponse(message=str(error))


@bind_exception(status.HTTP_500_INTERNAL_SERVER_ERROR)
def subscription_not_started_handler(
    _: requests.Request,
    error: service_exceptions.SubscriptionNotStarted,
) -> models.ErrorResponse:
    return models.ErrorResponse(message=str(error))


@bind_exception(status.HTTP_409_CONFLICT)
def already_chat_participant_handler(
    _: requests.Request,
    error: domain_exceptions.AlreadyChatParticipant,
) -> models.ErrorResponse:
    return models.ErrorResponse(message=str(error))


@bind_exception(status.HTTP_409_CONFLICT)
def duplicate_message_handler(
    _: requests.Request,
    error: domain_exceptions.DuplicateMessage,
) -> models.ErrorResponse:
    return models.ErrorResponse(message=str(error))


@bind_exception(status.HTTP_400_BAD_REQUEST)
def too_many_reactions_handler(
    _: requests.Request,
    error: domain_exceptions.TooManyReactions,
) -> models.ErrorResponse:
    return models.ErrorResponse(message=str(error))


@bind_exception(status.HTTP_400_BAD_REQUEST)
def emoji_validation_error_handler(
    _: requests.Request,
    error: EmojiValidationError,
) -> models.ErrorResponse:
    return models.ErrorResponse(message=str(error))
