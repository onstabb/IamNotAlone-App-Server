import tempfile


def test_upload_photo(user_factory, client, image_file):
    user = user_factory.create(photo_urls=[])
    client.bearer_token = user.token[0]
    data = {"photo": image_file}

    response = client.put(f"/api/v1/users/me/photos/0", files=data)

    assert response.status_code == 201


def test_upload_photo_incorrect_index(user_factory, client, image_file):
    user = user_factory.create(photo_urls=[])
    client.bearer_token = user.token[0]
    data = {"photo": image_file}

    response = client.put(f"/api/v1/users/me/photos/1", files=data)

    assert response.status_code == 404


def test_upload_profile_corrupted_photo(client, image_file, authorized_user):
    corrupted_file = tempfile.NamedTemporaryFile(suffix=".jpg", mode="w+b")
    corrupted_file.write( b'321mdmdmdam-m0m99889h9b98bb09j0nmmmvvbbnn' + image_file.read())
    data = {"photo": corrupted_file}

    response = client.put("/api/v1/users/me/photos/0", files=data)

    assert response.status_code == 406
