import logging
from logging import config

import fastapi
import fastapi_app
from fastapi_app import logging as fastapi_logging

import settings
from presentation.api.errors import handlers
from presentation.api.routes import healthcheck, v1

log_settings = settings.Logging()
app_settings = settings.App()

log_config = fastapi_logging.generate_log_config(
    logging_level=log_settings.LEVEL,
    serialize=log_settings.SERIALIZE,
    app_name=app_settings.NAME,
    app_version=settings.VERSION,
)

config.dictConfig(log_config)
logging.getLogger("asyncio").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("multipart").setLevel(logging.ERROR)
logging.getLogger("cqrs").setLevel(logging.ERROR)

api_router = fastapi.APIRouter(prefix="/api")
api_router.include_router(v1.router)

app = fastapi_app.create(
    debug=app_settings.DEBUG,
    title=app_settings.NAME,
    version=settings.VERSION,
    description="Messanger API",
    env_title=app_settings.ENV,
    query_routers=[healthcheck.router],
    command_routers=[api_router],
    exception_handlers=[
        handlers.message_not_found_handler,
        handlers.message_not_for_account_handler,
        handlers.chat_not_found_handler,
        handlers.attachment_already_sent_handler,
        handlers.attachment_already_uploaded_handler,
        handlers.attachment_not_found_handler,
        handlers.attachment_not_for_chat_handler,
        handlers.attachment_not_for_sender_handler,
        handlers.attachments_upload_error_handler,
        handlers.unsupported_voice_format_handler,
        handlers.not_participant_in_chat_handler,
        handlers.start_subscription_error_handler,
        handlers.subscription_not_started_handler,
        handlers.too_many_reactions_handler,
        handlers.emoji_validation_error_handler,
    ],
    cors_enable=True,
    log_config=log_config,
)
