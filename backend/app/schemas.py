from datetime import datetime

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


class WorkoutCreate(BaseModel):
    trained_at: datetime | None = None
    note: str | None = None


class WorkoutResponse(BaseModel):
    id: int
    trained_at: datetime
    note: str | None = None

    class Config:
        from_attributes = True


class WorkoutSetCreate(BaseModel):
    exercise_id: int
    weight: float
    reps: int
    set_order: int


class WorkoutSetResponse(BaseModel):
    id: int
    workout_id: int
    exercise_id: int
    weight: float
    reps: int
    set_order: int

    class Config:
        from_attributes = True


class WorkoutDetailResponse(BaseModel):
    id: int
    trained_at: datetime
    note: str | None = None
    sets: list[WorkoutSetResponse]

    class Config:
        from_attributes = True
