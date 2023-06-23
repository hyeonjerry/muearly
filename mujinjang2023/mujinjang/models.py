from django.db import models


class Product(models.Model):
    TIME_CHOICES = (
        ('00', '00:00'),
        ('10', '10:00'),
        ('14', '14:00'),
        ('18', '18:00'),
    )

    img = models.URLField()
    url = models.URLField()
    brand = models.CharField(max_length=50)
    sale_price = models.IntegerField()
    discount_rate = models.IntegerField()
    date = models.DateField()
    time = models.CharField(max_length=2, choices=TIME_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
