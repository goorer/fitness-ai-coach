from fastapi import FastAPI
from .database import engine, Base
from . import models

app = FastAPI()

# 起動時にテーブル作成
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "fitness-ai-coach API running"}