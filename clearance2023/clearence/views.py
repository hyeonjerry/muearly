from datetime import datetime

from django.shortcuts import render

from clearence.models import Product


def index(request):
    products = Product.objects.filter(created_at__lte=datetime.now()).order_by(
        '-discount_rate', '-normal_price')
    timesales = products.filter(discount_type='timesale')
    pricesales = products.filter(discount_type='pricesale')
    return render(request, 'index.html', {'timesales': timesales, 'pricesales': pricesales})
