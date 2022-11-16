from sqlalchemy.orm import Session
import datetime

from app.muearly import models


def get_today():
    return datetime.datetime.now().date()


def get_all_products(tab: str, db: Session):
    products = db.query(models.Product).filter(models.Product.tab == tab,
                                               models.Product.created_date == get_today()).all()
    return products
