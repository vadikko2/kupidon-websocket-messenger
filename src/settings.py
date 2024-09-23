import typing

import dotenv
import pydantic
import pydantic_settings

dotenv.load_dotenv()

VERSION = "0.0.6"


class Logging(pydantic_settings.BaseSettings, case_sensitive=True):
    """Logging config"""

    LEVEL: typing.Text = pydantic.Field(default="DEBUG")
    COLORIZE: bool = pydantic.Field(default=True)
    SERIALIZE: bool = pydantic.Field(default=False)

    model_config = pydantic_settings.SettingsConfigDict(env_prefix="LOGGING_")


class App(pydantic_settings.BaseSettings, case_sensitive=True):
    DEBUG: bool = pydantic.Field(default=False)
    NAME: typing.Text = pydantic.Field(default="messanger-api")
    ENV: typing.Text = pydantic.Field(default="local")
