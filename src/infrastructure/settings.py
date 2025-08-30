import dotenv
import pydantic
import pydantic_settings

dotenv.load_dotenv()


class S3Settings(pydantic_settings.BaseSettings, case_sensitive=True):
    ENDPOINT_URL: str = pydantic.Field(default="")
    REGION_NAME: str = pydantic.Field(default="")

    BUCKET_NAME: str = pydantic.Field(default="")
    PATH_PREFIX: str = pydantic.Field(default="")

    ACCESS_KEY_ID: str = pydantic.Field(default="")
    SECRET_ACCESS_KEY: str = pydantic.Field(default="")

    model_config = pydantic_settings.SettingsConfigDict(env_prefix="S3_")


s3_settings = S3Settings()
