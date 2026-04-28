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


class WorkoutSetUpdate(BaseModel):
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


class ExerciseSetHistoryResponse(BaseModel):
    id: int
    workout_id: int
    exercise_id: int
    trained_at: datetime
    weight: float
    reps: int
    set_order: int
    volume: float


class ExerciseSummaryResponse(BaseModel):
    exercise_id: int
    total_sets: int
    max_weight: float | None = None
    max_reps: int | None = None
    total_volume: float
    suggested_next_weight: float | None = None


class AIExerciseAnalysisRequest(BaseModel):
    goal: str | None = None
    model: str | None = None


class AIWorkoutAnalysisRequest(BaseModel):
    goal: str | None = None
    model: str | None = None


class AIExerciseAnalysisResponse(BaseModel):
    exercise_id: int
    exercise_name: str
    model: str
    history_count: int
    metrics: ExerciseSummaryResponse
    summary: str
    recommendation: str
    cautions: list[str]
    analysis: str


class AIWorkoutAnalysisResponse(BaseModel):
    workout_id: int
    model: str
    set_count: int
    total_volume: float
    summary: str
    recommendation: str
    cautions: list[str]
    analysis: str


class WorkoutDetailResponse(BaseModel):
    id: int
    trained_at: datetime
    note: str | None = None
    sets: list[WorkoutSetResponse]

    class Config:
        from_attributes = True
