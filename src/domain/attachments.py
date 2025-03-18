import datetime
import enum
import logging
import typing
import uuid

import cqrs
import pydantic

from domain import events

logger = logging.getLogger(__name__)


class AttachmentType(enum.StrEnum):
    """
    Attachment types
    """

    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"


class Attachment(pydantic.BaseModel):
    """
    Attachment entity
    """

    attachment_id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4, frozen=True)

    chat_id: uuid.UUID = pydantic.Field(frozen=True)
    uploader: typing.Text = pydantic.Field(frozen=True)

    created: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now,
        frozen=True,
    )
    uploaded: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)

    urls: typing.Sequence[pydantic.AnyHttpUrl] = pydantic.Field(default_factory=list)
    filename: typing.Optional[typing.Text] = pydantic.Field(
        default=None,
        max_length=100,
    )
    content_type: AttachmentType = pydantic.Field(frozen=True)

    event_list: typing.List[cqrs.DomainEvent] = pydantic.Field(
        default_factory=list,
        exclude=True,
    )

    def upload(
        self,
        urls: typing.List[pydantic.AnyHttpUrl],
        uploaded_dt: datetime.datetime | None = None,
    ) -> None:
        if uploaded_dt:
            self.uploaded = uploaded_dt

        self.urls = urls
        self.event_list.append(
            events.NewAttachmentUploaded(
                attachment_id=self.attachment_id,
                urls=self.urls,  # type: ignore
            ),
        )
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
