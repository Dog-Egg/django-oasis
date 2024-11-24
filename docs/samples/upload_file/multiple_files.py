from django_oasis import schema
from django_oasis.core import Resource
from django_oasis.parameter import FormItem


@Resource("/upload/multiple")
class UploadAPI:
    def post(
        self,
        files=FormItem(
            schema.List(
                schema.File(),
                max_items=3,  # 限制最多上传 3 个文件
            ),
        ),
    ):
        ...

        return {"contents": [f.read().decode() for f in files]}
