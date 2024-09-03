import logging
from logging import config

import fastapi_app
from fastapi_app import logging as fastapi_logging

import settings
from presentation.api import routes

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

app = fastapi_app.create(
    debug=app_settings.DEBUG,
    title=app_settings.NAME,
    version=settings.VERSION,
    description="Messanger API",
    env_title=app_settings.ENV,
    query_routers=[routes.chats.router, routes.subscription.router],
    command_routers=[routes.messages.router],
    cors_enable=True,
    log_config=log_config,
)
