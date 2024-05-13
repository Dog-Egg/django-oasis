from django_oasis import schema
from django_oasis.core import Resource
from django_oasis.parameter import FormData


@Resource("/upload")
class UploadAPI:
    def post(
        self,
        data=FormData(
            {
                "file": schema.File(),
            }
        ),
    ): ...


from django_oasis.core import OpenAPI

openapi = OpenAPI(title="Upload File")
openapi.add_resource(UploadAPI)
