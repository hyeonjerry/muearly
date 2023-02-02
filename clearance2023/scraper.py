import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

import requests
from bs4 import BeautifulSoup

from clearence.models import Product

store_url = 'https://www.musinsa.com/app/campaign/index/outlet_clearance_2023'


class TimesaleScraper:
    def __init__(self) -> None:
        self.soup = None
        self.items = []

    def get_price(self, tag):
        return int(tag.text.replace(',', ''))

    def get_rate(self, normal, sale):
        return round((normal - sale) / normal * 100)

    def set_soup(self):
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(store_url, headers=headers)
        self.soup = BeautifulSoup(response.text, 'html.parser')

    def set_items(self):
        item_selector = 'body > main > section > section:nth-child(3) > div > div.CTab__panel > div > div.list-container.column4 > div > div'
        self.items = self.soup.select(item_selector)

    def extract_data(self, item):
        prefix_url = 'https://www.musinsa.com'
        url_selector = 'div > a'
        img_selector = 'div > a > img'
        src_selector = 'data-original'
        brand_selector = 'a > span.CGoods__brand'
        name_selector = 'a > span.CGoods__name'
        sale_price_selector = 'a > div > span.CGoods__price__org'
        normal_price_selector = 'a > div > del'

        img = item.select_one(img_selector).get(src_selector)
        url = prefix_url + item.select_one(url_selector).get('href')
        brand = item.select_one(brand_selector).text
        name = item.select_one(name_selector).text
        sale_price = self.get_price(item.select_one(sale_price_selector))
        normal_price = self.get_price(item.select_one(normal_price_selector))
        discount_rate = self.get_rate(normal_price, sale_price)

        return Product(img=img, url=url, brand=brand, name=name, sale_price=sale_price, normal_price=normal_price, discount_rate=discount_rate, discount_type='timesale')

    def create_products(self):
        products = [self.extract_data(item) for item in self.items]
        Product.objects.bulk_create(products)

    def run(self):
        while not self.items:
            self.set_soup()
            self.set_items()
        self.create_products()
        self.items = []


ts = TimesaleScraper()
ts.run()
