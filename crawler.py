import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler

from muearly.models import Price
from muearly.models import Product

PRICE_URL = 'https://rcb.musinsa.com/total'
PRODUCT_URL = 'https://www.musinsa.com/app/blackfriday/special'
USER_AGENT = {'User-Agent':'Mozilla/5.0'}
last_updated_date = 0

block_sched = BlockingScheduler()
daemon_sched = BackgroundScheduler()


@daemon_sched.scheduled_job('interval', seconds=5, id='price')
def crawl_price():
    req = requests.get(PRICE_URL, headers=USER_AGENT).json()
    price = req['totalAmount']['purchase']
    Price.objects.create(price=price)


@block_sched.scheduled_job('cron', minute=5, id='product')
def crawl_product():
    req = requests.get(PRODUCT_URL, headers=USER_AGENT)
    soup = BeautifulSoup(req.text, 'html.parser')
    sessions = parse_sessions(soup)
    pannels = parse_pannels(soup)
    objects = []
    for session, pannel in zip(sessions, pannels):
        items = parse_items(pannel)
        objects.extend(get_objects(session, items))
    Product.objects.bulk_create(objects)


def parse_sessions(soup):
    session_selector = 'button.CTab__button.CTab__item.arriveSpecial__item'
    sessions = soup.select(session_selector)
    return [session.text.strip() for session in sessions]


def parse_pannels(soup):
    pannel_selector = 'section.CSection.CSection__arriveSpecial > div.CTab > div.CTab__panel'
    return soup.select(pannel_selector)


def parse_items(pannel):
    item_selector = 'div.list-container.column4 > div.list-item'
    return pannel.select(item_selector)


def get_object(item, session):
    src = item.select_one('img').get('data-original')
    if Product.objects.filter(src=src):
        return None
    brand = item.select_one('span.CGoods__brand').text
    discount = item.select_one('span.CGoods__price__rate').text
    price = item.select_one('span.CGoods__price__org').text.replace(',', '')
    quantity = item.select_one('span.CGoods__price__limit').text
    # TODO: url 파싱 구현
    return Product(src=src, brand=brand, discount=discount, price=price, limit_count=quantity, section=session)


def get_objects(session, items):
    objects = []
    for item in items:
        obj = get_object(item, session)
        if obj:
            objects.append(obj)
    return objects


if __name__ == '__main__':
    crawl_product()
    daemon_sched.start()
    block_sched.start()
