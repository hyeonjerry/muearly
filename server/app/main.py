from fastapi import FastAPI

from app.muearly import models
from app.muearly.database import engine
from app.muearly.routers import muearly
from app.muearly.crawler import sched

app = FastAPI()

models.Base.metadata.create_all(engine)

app.include_router(muearly.router)

sched.start()
