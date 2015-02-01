from django.db import models


class FooModel(models.Model):
    # WISHLIST one of every kind of field!
    # https://docs.djangoproject.com/en/dev/ref/models/fields/
    datetime = models.DateTimeField(null=True)
    decimal = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    slug = models.SlugField(max_length=5, null=True)
    text = models.TextField(null=True)
