import typing

import dotenv
import pydantic
import pydantic_settings

dotenv.load_dotenv()

VERSION = "0.0.1"


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


class Redis(pydantic_settings.BaseSettings, case_sensitive=True):
    URL: pydantic.RedisDsn = pydantic.Field(default="redis://localhost:6379")

    def dsn(self) -> typing.Text:
        return str(self.URL)

    model_config = pydantic_settings.SettingsConfigDict(env_prefix="REDIS_")
