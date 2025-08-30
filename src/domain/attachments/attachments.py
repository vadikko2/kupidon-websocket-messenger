import datetime
import enum
import logging
import typing
import uuid

import cqrs
import pydantic

from domain import events, exceptions

logger = logging.getLogger(__name__)


class AttachmentStatus(enum.StrEnum):
    NEW = "new"
    UPLOADED = "uploaded"
    SENT = "sent"
    DELETED = "deleted"


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
    message_sent_id: pydantic.UUID4 | None = None
    uploader: str = pydantic.Field(frozen=True)

    created: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now,
        frozen=True,
    )
    uploaded: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)
    sent: datetime.datetime | None = None

    status: AttachmentStatus = pydantic.Field(default=AttachmentStatus.NEW)

    urls: typing.Sequence[str] = pydantic.Field(default_factory=list)
    filename: str | None = pydantic.Field(
        default=None,
        max_length=100,
    )

    content_type: AttachmentType = pydantic.Field(frozen=True)
    meta: dict | None = pydantic.Field(default_factory=dict)

    event_list: list[cqrs.DomainEvent] = pydantic.Field(
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
        urls: list[str],
        uploaded_dt: datetime.datetime | None = None,
        meta: dict | None = None,
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
        logger.debug(f"Attachment {self.attachment_id} marks uploaded to chat {self.chat_id}")

        self.status = AttachmentStatus.UPLOADED

    def send(self, message_id: uuid.UUID) -> None:
        """
        Sends attachment
        """
        if self.sent or self.message_sent_id:
            raise exceptions.AttachmentAlreadySent(self.attachment_id)

        self.sent = datetime.datetime.now()
        self.message_sent_id = message_id

        self.event_list.append(
            events.AttachmentSent(
                message_id=message_id,
                attachment_id=self.attachment_id,
            ),
        )
        self.status = AttachmentStatus.SENT
        logger.debug(f"Attachment {self.attachment_id} sent with message {message_id}")

    def get_events(self) -> list[cqrs.DomainEvent]:
        """
        Returns new domain events
        """
        new_events = []
        while self.event_list:
            new_events.append(self.event_list.pop())
        return new_events

    def __hash__(self):
        return hash(self.attachment_id)
