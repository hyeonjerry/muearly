import uvicorn
from fastapi import FastAPI

from app.muearly import models
from app.muearly.database import engine

app = FastAPI()

models.Base.metadata.create_all(engine)


if __name__ == '__main__':
    uvicorn.run(app)
