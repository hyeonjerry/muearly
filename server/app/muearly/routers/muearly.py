from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.muearly import schemas, database
from app.muearly.repository import muearly

router = APIRouter(
    prefix='/api/v0/muearly',
    tags=['Muearly'],
)

get_db = database.get_db


@router.get('/products', response_model=List[schemas.Muearly])
def all(db: Session = Depends(get_db)):
    return muearly.get_all_products(db)
