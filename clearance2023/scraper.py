import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

import time
import requests
from bs4 import BeautifulSoup

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from clearence.models import Product

driver_path = '/usr/bin/chromedriver'
time_url = 'https://time.navyism.com/?host=www.musinsa.com'
store_url = 'https://www.musinsa.com/app/campaign/index/outlet_clearance_2023'

options = Options()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
service = Service(driver_path)


class Scraper:
    def __init__(self) -> None:
        self.driver = None
        self.soup = None
        self.items = []
        self.discount_type = ''

    def get_price(self, tag):
        return int(tag.text.replace(',', ''))

    def get_rate(self, normal, sale):
        return round((normal - sale) / normal * 100)

    def set_items(self, selector):
        self.items = self.soup.select(selector)

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

        return Product(img=img, url=url, brand=brand, name=name, sale_price=sale_price, normal_price=normal_price, discount_rate=discount_rate, discount_type=self.discount_type)

    def create_products(self):
        products = [self.extract_data(item) for item in self.items]
        Product.objects.bulk_create(products)


class TimesaleScraper(Scraper):
    def __init__(self) -> None:
        super().__init__()
        self.discount_type = 'timesale'

    def set_soup(self):
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(store_url, headers=headers)
        self.soup = BeautifulSoup(response.text, 'html.parser')

    def run(self):
        item_selector = 'body > main > section > section:nth-child(3) > div > div.CTab__panel > div > div.list-container.column4 > div > div'
        while not self.items:
            self.set_soup()
            self.set_items(item_selector)
        self.create_products()
        self.items = []


class PricesaleScraper(Scraper):
    def __init__(self) -> None:
        super().__init__()
        self.discount_type = 'pricesale'

    def set_driver(self):
        tab_selector = 'body > main > section > section:nth-child(5) > div > div.CTab__list > button:nth-child(%d)'
        if not self.driver:
            self.driver = Chrome(service=service, options=options)
        self.driver.get(store_url)
        for n in range(2, 5):
            try:
                self.driver.find_element(
                    By.CSS_SELECTOR, tab_selector % n).click()
            except:
                break

    def set_soup(self):
        time.sleep(0.1)
        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')

    def run(self):
        item_selector = 'body > main > section > section:nth-child(5) > div > div.CTab__panel > div:nth-child(2) > div.list-container.column4 > div.list-item'
        self.set_driver()
        self.set_soup()
        self.set_items(item_selector)
        self.create_products()
        self.driver.close()
        self.driver = None


ts = TimesaleScraper()
ps = PricesaleScraper()
ts.run()
ps.run()
