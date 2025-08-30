import dotenv
import pydantic
import pydantic_settings

dotenv.load_dotenv()


class RedisSettings(pydantic_settings.BaseSettings, case_sensitive=True):
    HOSTNAME: str = pydantic.Field(default="localhost")
    PORT: pydantic.PositiveInt = pydantic.Field(default=6379)
    DATABASE: pydantic.NonNegativeInt = pydantic.Field(default=0)
    USER: str = pydantic.Field(default="")
    PASSWORD: str = pydantic.Field(default="")

    def dsn(self) -> str:
        return f"redis://{self.USER}:{self.PASSWORD}@{self.HOSTNAME}:{self.PORT}/{self.DATABASE}"

    model_config = pydantic_settings.SettingsConfigDict(env_prefix="REDIS_")


redis_settings = RedisSettings()
