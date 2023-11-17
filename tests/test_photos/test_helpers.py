import pytest

from photos import helpers



@pytest.mark.parametrize(
    "filename",
    ["sub1.jpg", ]
)
def test_token_encoding(filename):
    data = {"filename": filename, "num": 322}
    encoded_filename = helpers.filename_token_encode(**data)
    decoded_data = helpers.filename_token_decode(encoded_filename)
    assert data == decoded_data


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://example.com/filename.jpg", "filename.jpg"),
        ("http://spmesite/path/to/file.doc", "file.doc"),
        ("http://localhost:80/2312d11d/FILE", "FILE"),
    ]
)
def test_get_image_filename_from_url(url, expected):
    assert helpers.get_image_filename_from_url(url) == expected


def test_check_image_is_valid(image_file):
    assert helpers.check_image_is_valid(image_file)


def test_compress(image_file):
    def get_file_size(file_obj) -> int:
        file_obj.seek(0, 2)
        return file_obj.tell()

    compressed_image = helpers.image_compress(image_file)
    assert compressed_image
    assert get_file_size(compressed_image) <= get_file_size(image_file)