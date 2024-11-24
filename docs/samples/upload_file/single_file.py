from django_oasis import schema
from django_oasis.core import Resource
from django_oasis.parameter import FormItem


@Resource("/upload/single")
class UploadAPI:
    def post(
        self,
        file=FormItem(schema.File()),
    ):
        ...

        from django.core.files.uploadedfile import InMemoryUploadedFile

        assert file.__class__ is InMemoryUploadedFile, file.__class__
        return file.read()
