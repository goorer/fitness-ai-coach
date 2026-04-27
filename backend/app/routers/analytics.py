from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(tags=["Analytics"])


@router.get(
    "/exercises/{exercise_id}/history",
    response_model=list[schemas.ExerciseSetHistoryResponse],
)
def get_exercise_history(
    exercise_id: int,
    db: Session = Depends(get_db),
):
    db_exercise = db.get(models.Exercise, exercise_id)

    if not db_exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    rows = (
        db.query(models.WorkoutSet, models.Workout)
        .join(models.Workout, models.WorkoutSet.workout_id == models.Workout.id)
        .filter(models.WorkoutSet.exercise_id == exercise_id)
        .order_by(models.Workout.trained_at.asc(), models.WorkoutSet.set_order.asc())
        .all()
    )

    return [
        {
            "id": workout_set.id,
            "workout_id": workout_set.workout_id,
            "exercise_id": workout_set.exercise_id,
            "trained_at": workout.trained_at,
            "weight": workout_set.weight,
            "reps": workout_set.reps,
            "set_order": workout_set.set_order,
            "volume": workout_set.weight * workout_set.reps,
        }
        for workout_set, workout in rows
    ]


@router.get(
    "/exercises/{exercise_id}/summary",
    response_model=schemas.ExerciseSummaryResponse,
)
def get_exercise_summary(
    exercise_id: int,
    db: Session = Depends(get_db),
):
    db_exercise = db.get(models.Exercise, exercise_id)

    if not db_exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    workout_sets = (
        db.query(models.WorkoutSet)
        .filter(models.WorkoutSet.exercise_id == exercise_id)
        .all()
    )

    if not workout_sets:
        return {
            "exercise_id": exercise_id,
            "total_sets": 0,
            "max_weight": None,
            "max_reps": None,
            "total_volume": 0,
            "suggested_next_weight": None,
        }

    max_weight = max(workout_set.weight for workout_set in workout_sets)
    max_reps = max(workout_set.reps for workout_set in workout_sets)
    total_volume = sum(
        workout_set.weight * workout_set.reps for workout_set in workout_sets
    )

    return {
        "exercise_id": exercise_id,
        "total_sets": len(workout_sets),
        "max_weight": max_weight,
        "max_reps": max_reps,
        "total_volume": total_volume,
        "suggested_next_weight": max_weight + 2.5,
    }
