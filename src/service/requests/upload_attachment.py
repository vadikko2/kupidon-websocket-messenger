import uuid

import cqrs
import pydantic


class AttachmentUploaded(cqrs.Response):
    attachment_id: uuid.UUID
    url: pydantic.AnyHttpUrl
