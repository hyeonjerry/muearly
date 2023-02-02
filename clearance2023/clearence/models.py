from django.db import models


class Product(models.Model):
    img = models.URLField()
    url = models.URLField()
    brand = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    sale_price = models.IntegerField()
    normal_price = models.IntegerField()
    discount_rate = models.IntegerField()
    discount_type = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
