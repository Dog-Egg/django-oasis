from django_oasis import Resource, schema
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


from django_oasis import OpenAPI

openapi = OpenAPI(title="Upload File")
openapi.add_resource(UploadAPI)
