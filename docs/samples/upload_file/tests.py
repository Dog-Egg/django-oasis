import io

import pytest

from django_oasis.urls import reverse

from . import multiple_files, single_file, urls


@pytest.mark.urls(urls)
def test_upload_single_file(client):
    """上传单文件"""
    file = io.StringIO("Hello 123")
    response = client.post(reverse(single_file.UploadAPI), data={"file": file})
    assert response.content == b"Hello 123"


@pytest.mark.urls(urls)
def test_upload_multiple_files(client):
    """上传多个文件"""
    files = [io.StringIO(f"Hello {i}") for i in range(4)]
    response = client.post(
        reverse(multiple_files.UploadAPI),
        data={"files": files},
    )
    assert response.status_code == 400
    assert response.json() == {
        "validation_errors": [
            {
                "loc": [
                    "files",
                ],
                "msgs": [
                    "The length must be less than or equal to 3.",
                ],
            },
        ],
    }

    files = [io.StringIO(f"Hello {i}") for i in range(3)]
    response = client.post(
        reverse(multiple_files.UploadAPI),
        data={"files": files},
    )
    assert response.json() == {"contents": ["Hello 0", "Hello 1", "Hello 2"]}
