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
USER_AGENT = {'User-Agent': 'Mozilla/5.0'}
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
    pannels = parse_pannels()
    objects = []
    for session, pannel in pannels.items():
        items = parse_items(pannel)
        objects.extend(get_objects(session, items))
    Product.objects.bulk_create(objects)


def parse_pannels():
    req = requests.get(PRODUCT_URL, headers=USER_AGENT)
    soup = BeautifulSoup(req.text, 'html.parser')
    sessions = parse_sessions(soup)
    tab_uids = get_tab_uids(sessions)
    pannels = get_pannels(tab_uids)
    return {session.text.strip(): pannel for session, pannel in zip(sessions, pannels)}


def parse_sessions(soup):
    session_selector = 'div.CTab__list.arriveSpecial__list > button.CTab__button'
    return soup.select(session_selector)


def get_tab_uids(sessions):
    uids = []
    for session in sessions:
        onclick = session.get('onclick')
        uid = onclick[onclick.find("'")+1:onclick.find(",")-1]
        uids.append(uid)
    return uids


def get_pannels(uids):
    url = 'https://www.musinsa.com/app/blackfriday/get_campaign_tab_data'
    datas = [{'tab_uid': uid} for uid in uids]
    pannels = []
    for data in datas:
        req = requests.post(url, data=data, headers=USER_AGENT)
        source = convert_unicode_escape(req.text)
        soup = BeautifulSoup(source, 'html.parser')
        pannels.append(soup)
    return pannels


def convert_unicode_escape(source):
    bytes_source = source.encode('utf-8')
    text = bytes_source.decode('unicode_escape')
    text = text.replace('\\/', '/')
    return text


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
