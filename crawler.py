import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
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

options = Options()
options.add_argument('headless')
options.add_argument('--window-size=1920,1080')
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 60)

block_sched = BlockingScheduler()
daemon_sched = BackgroundScheduler()


def wait_select(selector):
    return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))


def wait_selects(selector):
    return wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))


@daemon_sched.scheduled_job('interval', seconds=5, id='price')
def crawl_price():
    req = requests.get(PRICE_URL, USER_AGENT).json()
    price = req['totalAmount']['purchase']
    Price.objects.create(price=price)


@block_sched.scheduled_job('cron', hour=12, minute=5, id='product')
def crawl_product():
    driver.get(PRODUCT_URL)
    # 시간 섹션 조회
    sections = get_sections()
    for section in sections:
        section.click()
        # 더보기
        click_show_more()
        # 상품 조회
        source = driver.page_source
        items = parse_items(source, section.text)
        Product.objects.bulk_create(items)


def get_sections():
    section_selector = 'button.CTab__button.CTab__item.arriveSpecial__item'
    return wait_selects(section_selector)


def click_show_more():
    more_selector = 'a.CButton.CButton--radius.CButton--more'
    wait_select(more_selector).click()


def get_items():
    item_selector = 'div.CTab > div:nth-child(5) > div:nth-child(1) > div.list-container.column4 > div.list-item > div.CGoods'
    return wait_selects(item_selector)


def parse_items(source, section):
    item_selector = 'div.CTab > div:nth-child(5) > div:nth-child(1) > div.list-container.column4 > div.list-item > div.CGoods'
    soup = BeautifulSoup(source, 'html.parser')
    items = soup.select(item_selector)
    result = []
    for item in items:
        brand = item.select_one('span.CGoods__brand').text
        src = item.select_one('img').get('data-original')
        limit_count = item.select_one('span.CGoods__price__limit').text
        price = item.select_one('span.CGoods__price__org').text.replace(',', '')
        discount = item.select_one('span.CGoods__price__rate').text
        result.append(Product(brand=brand, src=src, limit_count=limit_count, price=price, discount=discount, section=section))
    return result


if __name__ == '__main__':
    daemon_sched.start()
    block_sched.start()
