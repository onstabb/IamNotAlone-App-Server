import pytest

from photos import helpers



@pytest.mark.parametrize(
    "filename",
    ["sub1.jpg", ]
)
def test_token_encoding(filename):
    data = {"filename": filename, "num": 322}
    encoded_filename = helpers.filename_token_encode("jpg", **data)
    decoded_data = helpers.filename_token_decode(encoded_filename)
    assert data == decoded_data


def test_check_image_is_valid(image_file):
    assert helpers.check_image_is_valid(image_file)


def test_compress(image_file):
    def get_file_size(file_obj) -> int:
        file_obj.seek(0, 2)
        return file_obj.tell()

    compressed_image = helpers.image_compress(image_file)
    assert compressed_image
    assert get_file_size(compressed_image) <= get_file_size(image_file)