import datetime
import enum
import logging
import typing
import uuid

import cqrs
import pydantic

from domain import events, exceptions

logger = logging.getLogger(__name__)


class AttachmentType(enum.StrEnum):
    """
    Attachment types
    """

    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"

    CIRCLE = "circle"
    VOICE = "voice"
    STICKER = "sticker"


class Attachment(pydantic.BaseModel):
    """
    Attachment entity
    """

    attachment_id: pydantic.UUID4 = pydantic.Field(default_factory=uuid.uuid4, frozen=True)

    chat_id: pydantic.UUID4 = pydantic.Field(frozen=True)
    uploader: typing.Text = pydantic.Field(frozen=True)

    created: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now,
        frozen=True,
    )
    uploaded: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)

    urls: typing.Sequence[str] = pydantic.Field(default_factory=list)
    filename: typing.Optional[typing.Text] = pydantic.Field(
        default=None,
        max_length=100,
    )

    content_type: AttachmentType = pydantic.Field(frozen=True)
    meta: typing.Dict | None = pydantic.Field(default_factory=dict)

    event_list: typing.List[cqrs.DomainEvent] = pydantic.Field(
        default_factory=list,
        exclude=True,
    )

    @pydantic.model_validator(mode="after")
    def check_fields(self):
        if self.meta is None:
            self.meta = {}

        return self

    def upload(
        self,
        urls: typing.List[typing.Text],
        uploaded_dt: datetime.datetime | None = None,
        meta: typing.Dict | None = None,
    ) -> None:
        """
        Uploads attachment
        """
        if uploaded_dt:
            self.uploaded = uploaded_dt

        if self.meta or self.urls:
            raise exceptions.AttachmentAlreadyUploaded(self.attachment_id)

        self.urls = urls
        self.event_list.append(
            events.NewAttachmentUploaded(
                attachment_id=self.attachment_id,
                urls=self.urls,  # type: ignore
            ),
        )
        if meta is None:
            meta = {}

        self.meta = meta
        logger.info(f"Attachment marks as uploaded: {self.attachment_id}")

    def get_events(self) -> typing.List[cqrs.DomainEvent]:
        """
        Returns new domain events
        """
        new_events = []
        while self.event_list:
            new_events.append(self.event_list.pop())
        return new_events

    def __hash__(self):
        return hash(self.attachment_id)
