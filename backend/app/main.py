from fastapi import FastAPI

from . import models
from .database import Base, engine
from .routers import exercises, workouts

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(exercises.router)
app.include_router(workouts.router)


@app.get("/")
def root():
    return {"message": "fitness-ai-coach API running"}
