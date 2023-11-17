import typing
from functools import cached_property

import boto3

from photos import config
from photos.bucket.base import BaseBucket


class S3Bucket(BaseBucket):

    @cached_property
    def client(self):
        return boto3.client(
            "s3",
            endpoint_url=config.S3_API_ENDPOINT,
            aws_access_key_id=config.S3_ACCESS_KEY_ID,
            aws_secret_access_key=config.S3_SECRET_ACCESS_KEY_ID
        )

    def upload(self, file: typing.BinaryIO, filename: str, **kwargs) -> str:
        response: dict = self.client.put_object(
            Bucket=config.S3_BUCKET_NAME, Body=file.read(), Key=filename, **kwargs
        )
        return f"{config.S3_IPFS_URL}/{response['ResponseMetadata']['HTTPHeaders']['x-amz-meta-cid']}"
