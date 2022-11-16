from sqlalchemy.orm import Session

from app.muearly import models


def get_all_products(db: Session):
    products = db.query(models.Product).all()
    return products
