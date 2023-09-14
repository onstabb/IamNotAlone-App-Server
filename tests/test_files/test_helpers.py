import pytest

from files import helpers



@pytest.mark.parametrize(
    "subject",
    ["sub1", ]
)
def test_token_encoding(subject):
    token = helpers.file_token_create(subject)
    decoded_sub, created_at = helpers.file_token_decode(token)
    assert decoded_sub == subject


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
