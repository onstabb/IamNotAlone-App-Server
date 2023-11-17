from photos.bucket.aws import S3Bucket
from photos.bucket.local import LocalBucket


def test_aws_bucket_upload(image_file):
    file_service = S3Bucket()
    url = file_service.upload(image_file, 'Test1.jpg', ContentType="image/jpeg")
    assert url


def test_local_bucket_upload(image_file):
    file_service = LocalBucket()
    url = file_service.upload(image_file, 'Test1.jpg', ContentType="image/jpeg")
    assert url
