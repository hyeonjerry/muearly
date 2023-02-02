from pydantic import BaseModel


class MuearlyBase(BaseModel):
    src: str
    url: str
    brand: str
    discount: int
    price: int
    quantity: int


class Muearly(MuearlyBase):
    class Config():
        orm_mode = True
