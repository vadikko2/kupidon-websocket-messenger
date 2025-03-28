import typing

import dotenv
import pydantic
import pydantic_settings

dotenv.load_dotenv()


class S3Settings(pydantic_settings.BaseSettings, case_sensitive=True):
    ENDPOINT_URL: typing.Text = pydantic.Field(default="")
    REGION_NAME: typing.Text = pydantic.Field(default="")

    BUCKET_NAME: typing.Text = pydantic.Field(default="")
    PATH_PREFIX: typing.Text = pydantic.Field(default="")

    ACCESS_KEY_ID: typing.Text = pydantic.Field(default="")
    SECRET_ACCESS_KEY: typing.Text = pydantic.Field(default="")

    model_config = pydantic_settings.SettingsConfigDict(env_prefix="S3_")


s3_settings = S3Settings()
