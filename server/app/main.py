import uvicorn
from fastapi import FastAPI

from app.muearly import models
from app.muearly.database import engine
from app.muearly.routers import muearly

app = FastAPI()

models.Base.metadata.create_all(engine)

app.include_router(muearly.router)


if __name__ == '__main__':
    uvicorn.run(app)
