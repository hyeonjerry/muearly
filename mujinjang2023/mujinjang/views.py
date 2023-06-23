from django.shortcuts import render
from mujinjang.models import Product
from datetime import date


def index(request, time):
    products = Product.objects.filter(date=date.today(), time=time)\
        .order_by('-discount_rate', 'sale_price')
    context = {'time': time, 'products': products}
    return render(request, 'index.html', context=context)
