import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler

from sqlalchemy.orm import Session
from app.muearly import database
from app.muearly.models import Product

PRICE_URL = 'https://rcb.musinsa.com/total'
PRODUCT_URL = 'https://www.musinsa.com/app/blackfriday/special'
HEADERS = {'User-Agent': 'Mozilla/5.0'}

sched = BackgroundScheduler()
session = database.Session
db: Session = session()


@sched.scheduled_job('cron', second=5, id='product')
def crawl_product():
    sections = get_sections()
    objects = []
    for tab, pannel in sections.items():
        items = get_items(pannel)
        objects.extend(get_objects(tab, items))
    db.add_all(objects)
    db.commit()


def get_sections():
    request = requests.get(PRODUCT_URL, headers=HEADERS)
    parser = BeautifulSoup(request.text, 'html.parser')
    tabs = get_tabs(parser)
    uids = get_uids(tabs)
    pannels = get_pannels(uids)
    return {tab.text.strip(): pannel for tab, pannel in zip(tabs, pannels)}


def get_tabs(parser):
    tab_selector = 'div.CTab__list.arriveSpecial__list > button.CTab__button'
    return parser.select(tab_selector)


def get_uids(tabs):
    uids = []
    for tab in tabs:
        onclick = tab.get('onclick')
        uid = onclick[onclick.find("'")+1:onclick.find(",")-1]
        uids.append(uid)
    return uids


def get_pannels(uids):
    url = 'https://www.musinsa.com/app/blackfriday/get_campaign_tab_data'
    datas = [{'tab_uid': uid} for uid in uids]
    pannels = []
    for data in datas:
        request = requests.post(url, data=data, headers=HEADERS)
        source = convert_unicode_escape(request.text)
        parser = BeautifulSoup(source, 'html.parser')
        pannels.append(parser)
    return pannels


def convert_unicode_escape(source):
    bytes_source = source.encode('utf-8')
    text = bytes_source.decode('unicode_escape')
    text = text.replace('\\/', '/')
    return text


def get_items(pannel):
    item_selector = 'div.list-container.column4 > div.list-item'
    return pannel.select(item_selector)


def get_object(tab, item):
    src = item.select_one('img').get('data-original')
    if db.query(Product).filter(Product.src == src).first():
        return None
    brand = item.select_one('span.CGoods__brand').text
    discount = item.select_one('span.CGoods__price__rate').text
    price = item.select_one('span.CGoods__price__org').text.replace(',', '')
    quantity = item.select_one('span.CGoods__price__limit').text
    # TODO: url 파싱 구현
    return Product(src=src, brand=brand, discount=discount, price=price, quantity=quantity, tab=tab)


def get_objects(tab, items):
    objects = []
    for item in items:
        obj = get_object(tab, item)
        if obj:
            objects.append(obj)
    return objects
