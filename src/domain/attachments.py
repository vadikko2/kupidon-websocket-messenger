import datetime
import enum
import typing
import uuid

import cqrs
import pydantic

from domain import events


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
    uploaded: datetime.datetime | None = pydantic.Field(default=None)

    urls: typing.List[typing.Text] = pydantic.Field(default_factory=list)
    filename: typing.Optional[typing.Text] = pydantic.Field(
        default=None,
        max_length=100,
    )
    content_type: AttachmentType = pydantic.Field(frozen=True)

    event_list: typing.List[cqrs.DomainEvent] = pydantic.Field(default_factory=list)

    def upload(
        self,
        urls: typing.List[typing.Text],
        uploaded_dt: datetime.datetime | None = None,
    ) -> None:
        self.uploaded = uploaded_dt or datetime.datetime.now()
        self.urls = urls
        self.event_list.append(
            events.NewAttachmentUploaded(
                attachment_id=self.attachment_id,
                urls=self.urls,  # type: ignore
            ),
        )

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
