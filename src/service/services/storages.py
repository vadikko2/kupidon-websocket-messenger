import logging
import typing

from service import exceptions
from service.interfaces import attachment_storage

logger = logging.getLogger(__name__)


async def upload_file_to_storage(
    storage: attachment_storage.AttachmentStorage,
    file_object: typing.BinaryIO,
    filename: typing.Text,
) -> typing.Text:
    """Uploads file to storage and returns its URL"""
    try:
        file_object.seek(0)
        url = await storage.upload(file_object, filename)
    except Exception as e:
        raise exceptions.AttachmentUploadError(e)

    logger.info(f"Uploaded attachment: {url}")
    return url
