from django.db import models


class Price(models.Model):
    price = models.IntegerField()
    created_date = models.DateTimeField(auto_now_add=True)


class Product(models.Model):
    brand = models.CharField(max_length=100)
    src = models.URLField()
    limit_count = models.IntegerField()
    price = models.IntegerField()
    discount = models.IntegerField()
    section = models.CharField(max_length=6)
    created_date = models.DateTimeField(auto_now_add=True)
