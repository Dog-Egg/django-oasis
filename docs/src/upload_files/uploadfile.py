from django_oasis import Resource, schema
from django_oasis.parameter import FormItem


@Resource("/upload")
class UploadAPI:
    def post(
        self,
        file=FormItem(schema.File),
    ):
        ...


from django_oasis import OpenAPI

openapi = OpenAPI(title="Upload File")
openapi.add_resource(UploadAPI)
