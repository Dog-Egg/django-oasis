from django.db import models


class Book(models.Model):
    title = models.CharField("书名", max_length=20)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
