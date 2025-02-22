import typing

import pydantic


class Check(pydantic.BaseModel, frozen=True):
    name: typing.Text = pydantic.Field(
        description="Название проверки",
        examples=["mysql", "redis", "kafka", "billing-configurations"],
    )
    healthy: bool = pydantic.Field(default=True)
    error: typing.Text = pydantic.Field(
        description="Сообщение об ошибке",
        default="",
    )

    def __bool__(self):
        return self.healthy


class Healthcheck(pydantic.BaseModel, frozen=True):
    checks: typing.List[Check] = pydantic.Field(
        description="Список проверок",
        default_factory=list,
    )

    @pydantic.computed_field()
    def healthy(self) -> bool:
        return all(self.checks)

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)
