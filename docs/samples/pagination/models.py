from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=10, verbose_name="书名")
    author = models.CharField(max_length=20, verbose_name="作者")
