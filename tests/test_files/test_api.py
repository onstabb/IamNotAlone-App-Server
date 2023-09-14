
from tempfile import NamedTemporaryFile

from test_files.conftest import get_image_path


def test_upload_photo(client, authorization_user_only):
    data = {"photo": open(get_image_path("Test1.jpg"), "rb",)}
    response = client.put("/api/v1/files/photo", files=data, headers=authorization_user_only)
    assert response.status_code == 201


def test_upload_corrupted_image(client, authorization_user_only):
    temp_file = NamedTemporaryFile(suffix=".jpg", mode="a+b")
    with open(get_image_path("Test1.jpg"), "rb") as real_file:
        temp_file.write( b'321mdmdmdam-m0m99889h9b98bb09j0nmmmvvbbnn' + real_file.read())

    data = {"photo": temp_file}
    response = client.put("/api/v1/files/photo", files=data, headers=authorization_user_only)
    assert response.status_code == 406
