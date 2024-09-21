import logging
import typing

import boto3.session
from botocore import client

from infrastructure import settings
from infrastructure.storages import attachment_storage

logging.getLogger("botocore").setLevel(logging.ERROR)
logging.getLogger("s3transfer").setLevel(logging.ERROR)
logging.getLogger("boto3").setLevel(logging.ERROR)


class S3AttachmentStorage(attachment_storage.AttachmentStorage):
    def __init__(self):
        self.endpoint_url = settings.s3_settings.ENDPOINT_URL
        self.region_name = settings.s3_settings.REGION_NAME

        self.bucket_name = settings.s3_settings.BUCKET_NAME
        self.path_prefix = settings.s3_settings.PATH_PREFIX

        self.access_key_id = settings.s3_settings.ACCESS_KEY_ID
        self.secret_access_key = settings.s3_settings.SECRET_ACCESS_KEY

    def _generate_download_url(self, filename: typing.Text) -> typing.Text:
        return self.endpoint_url + "/" + self.bucket_name + "/" + filename

    async def upload(
        self,
        attachment: typing.BinaryIO,
        filename: typing.Text,
    ) -> typing.Text:
        full_filename = (
            f"{self.path_prefix}/{filename}" if self.path_prefix else filename
        )

        session = boto3.session.Session()
        s3: client.BaseClient = session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            region_name=self.region_name,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
        )

        s3.upload_fileobj(
            attachment,
            self.bucket_name,
            full_filename,
        )
        return self._generate_download_url(full_filename)
