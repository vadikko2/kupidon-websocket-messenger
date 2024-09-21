import typing

import dotenv
import pydantic
import pydantic_settings

dotenv.load_dotenv()


class RedisSettings(pydantic_settings.BaseSettings, case_sensitive=True):
    HOSTNAME: typing.Text = pydantic.Field(default="localhost")
    PORT: pydantic.PositiveInt = pydantic.Field(default=6379)
    DATABASE: pydantic.NonNegativeInt = pydantic.Field(default=0)
    USER: typing.Text = pydantic.Field(default="")
    PASSWORD: typing.Text = pydantic.Field(default="")

    def dsn(self) -> typing.Text:
        return f"redis://{self.USER}:{self.PASSWORD}@{self.HOSTNAME}:{self.PORT}/{self.DATABASE}"

    model_config = pydantic_settings.SettingsConfigDict(env_prefix="REDIS_")


class S3Settings(pydantic_settings.BaseSettings, case_sensitive=True):
    ENDPOINT_URL: typing.Text = pydantic.Field(default="")
    REGION_NAME: typing.Text = pydantic.Field(default="")

    BUCKET_NAME: typing.Text = pydantic.Field(default="")
    PATH_PREFIX: typing.Text = pydantic.Field(default="")

    ACCESS_KEY_ID: typing.Text = pydantic.Field(default="")
    SECRET_ACCESS_KEY: typing.Text = pydantic.Field(default="")

    model_config = pydantic_settings.SettingsConfigDict(env_prefix="S3_")


redis_settings = RedisSettings()
s3_settings = S3Settings()
