from django_oasis import Resource


@Resource("/to/path")
class API:
    def head(self):
        """HEAD Operation"""

    def options(self):
        """OPTIONS Operation"""

    def get(self):
        """GET Operation"""

    def post(self):
        """POST Operation"""

    def put(self):
        """PUT Operation"""

    def patch(self):
        """PATCH Operation"""

    def delete(self):
        """DELETE Operation"""

    def trace(self):
        """TRACE Operation"""
