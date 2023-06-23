import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from datetime import date
from apscheduler.schedulers.blocking import BlockingScheduler

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from mujinjang.models import Product

STORE_URL = 'https://www.musinsa.com/app/mujinjangsale/special'
PRODUCT_URL = 'https://www.musinsa.com/app/api/mujinjangsale/get_campaign_tab_data'
HEADERS = {'User-Agent': 'Mozilla/5.0'}

sched = BlockingScheduler()


def get_uids() -> dict:
    button_selector = 'body > main > div > section.content > div > section.CSection.arriveSpecial > div > div.CTab__list > button'
    times = [time[0] for time in Product.TIME_CHOICES]
    response = requests.get(STORE_URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    buttons = soup.select(button_selector)
    return {time: button.get('tab-uid')
            for time, button in zip(times, buttons)}


def _parse_to_product(item: Tag, time: str) -> Product:
    url_prefix = 'https://www.musinsa.com'
    img = item.select_one('img').get('data-src')
    url = url_prefix + item.get('href')
    brand = item.select_one('div.arriveSpecial-goods__brand').text
    sale_price = item.select_one('div.arriveSpecial-goods__price__normal')\
        .text.replace(',', '').replace('원', '')
    discount_rate = item.select_one('span.arriveSpecial-goods__price__rate')\
        .text.replace('%', '')
    return Product(img=img, url=url, brand=brand, sale_price=sale_price, discount_rate=discount_rate, date=date.today(), time=time)


def _convert_unicode_escape(source: str) -> str:
    bytes_source = source.encode('utf-8')
    text = bytes_source.decode('unicode_escape')
    text = text.replace('\\', '').replace('\t', '').replace('\n', '')
    return text


def fetch_products(time: str, uid: str) -> list:
    item_selector = 'a.arriveSpecial-goods__item'
    response = requests.post(
        PRODUCT_URL, headers=HEADERS, data={'tab_uid': uid})
    source = _convert_unicode_escape(response.text)
    soup = BeautifulSoup(source, 'html.parser')
    items = soup.select(item_selector)
    products = [_parse_to_product(item, time) for item in items]
    return products


def run():
    uids = get_uids()
    for time, uid in uids.items():
        products = fetch_products(time, uid)
        Product.objects.bulk_create(products)


if __name__ == '__main__':
    sched.add_job(run, 'cron', hour=0, minute=5)
    sched.start()
