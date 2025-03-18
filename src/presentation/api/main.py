import logging
from logging import config

import fastapi_app
import socketio
from fastapi_app import logging as fastapi_logging

import settings
from presentation.api import errors, routes
from presentation.api.routes.v2.subscription import sio

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

app = fastapi_app.create(
    debug=app_settings.DEBUG,
    title=app_settings.NAME,
    version=settings.VERSION,
    description="Messanger API",
    env_title=app_settings.ENV,
    query_routers=[
        routes.v1_router,
        routes.v2_router,
        routes.healthcheck.router,
    ],
    exception_handlers=[
        errors.handlers.message_not_found_handler,
        errors.handlers.chat_not_found_handler,
        errors.handlers.attachment_not_found_handler,
        errors.handlers.attachment_not_for_chat_handler,
        errors.handlers.attachment_not_for_sender_handler,
        errors.handlers.not_participant_in_chat_handler,
        errors.handlers.start_subscription_error_handler,
        errors.handlers.subscription_not_started_handler,
        errors.handlers.too_many_reactions_handler,
        errors.handlers.emoji_validation_error_handler,
    ],
    cors_enable=True,
    log_config=log_config,
)

# Socket.IO
socketio_app = socketio.ASGIApp(socketio_server=sio, other_asgi_app=app)
app.add_route("/socket.io/", route=socketio_app, methods=["GET", "POST"])  # pyright: ignore[reportArgumentType]
app.add_websocket_route("/socket.io/", socketio_app)  # pyright: ignore[reportArgumentType]
