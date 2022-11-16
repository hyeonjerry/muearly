from sqlalchemy import Column, Integer, String

from app.muearly.database import Base


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    src = Column(String(250))
    url = Column(String(250), default="#")
    brand = Column(String(30))
    discount = Column(Integer)
    price = Column(Integer)
    quantity = Column(Integer)
