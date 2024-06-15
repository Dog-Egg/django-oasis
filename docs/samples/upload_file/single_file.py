from django_oasis import schema
from django_oasis.core import Resource
from django_oasis.parameter import FormData


@Resource("/upload/single")
class UploadAPI:
    def post(
        self,
        data=FormData(
            {
                "file": schema.File(),
            }
        ),
    ):
        ...

        from django.core.files.uploadedfile import InMemoryUploadedFile

        file = data["file"]
        assert file.__class__ is InMemoryUploadedFile, file.__class__
        return file.read()
