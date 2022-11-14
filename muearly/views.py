import datetime as dt

from django.shortcuts import render

from muearly.models import Price
from muearly.models import Product


def get_today():
    return dt.datetime.now().date().strftime('%Y%m%d')


def convert_str_to_date(date):
    if date == '':
        return dt.datetime.now()
    return dt.datetime(date, '%Y%m%d')


def index(requests):
    time = requests.GET.get('time', '00') + ':00'
    date = convert_str_to_date(requests.GET.get('date', ''))
    items = Product.objects.all().filter(created_date=date, section=time)
    context = {'items': items}
    return render(requests, 'index.html', context)
