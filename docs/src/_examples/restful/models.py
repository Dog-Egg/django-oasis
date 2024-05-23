from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=50, verbose_name="标题")
    author = models.CharField(max_length=50, verbose_name="作者")
