from pydantic import BaseModel


class ExerciseCreate(BaseModel):
    name: str
    body_part: str | None = None


class ExerciseResponse(BaseModel):
    id: int
    name: str
    body_part: str | None = None

    class Config:
        from_attributes = True