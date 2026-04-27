from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(tags=["Workouts"])


@router.post("/workouts", response_model=schemas.WorkoutResponse)
def create_workout(
    workout: schemas.WorkoutCreate,
    db: Session = Depends(get_db),
):
    db_workout = models.Workout(note=workout.note)

    if workout.trained_at:
        db_workout.trained_at = workout.trained_at

    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)

    return db_workout


@router.get("/workouts", response_model=list[schemas.WorkoutResponse])
def get_workouts(db: Session = Depends(get_db)):
    return db.query(models.Workout).all()


@router.get("/workouts/{workout_id}", response_model=schemas.WorkoutDetailResponse)
def get_workout(
    workout_id: int,
    db: Session = Depends(get_db),
):
    db_workout = db.query(models.Workout).get(workout_id)

    if not db_workout:
        return None

    workout_sets = (
        db.query(models.WorkoutSet)
        .filter(models.WorkoutSet.workout_id == workout_id)
        .order_by(models.WorkoutSet.set_order.asc())
        .all()
    )

    return {
        "id": db_workout.id,
        "trained_at": db_workout.trained_at,
        "note": db_workout.note,
        "sets": workout_sets,
    }


@router.post("/workouts/{workout_id}/sets", response_model=schemas.WorkoutSetResponse)
def create_workout_set(
    workout_id: int,
    workout_set: schemas.WorkoutSetCreate,
    db: Session = Depends(get_db),
):
    db_workout = db.query(models.Workout).get(workout_id)

    if not db_workout:
        return None

    db_exercise = db.query(models.Exercise).get(workout_set.exercise_id)

    if not db_exercise:
        return None

    db_workout_set = models.WorkoutSet(
        workout_id=workout_id,
        exercise_id=workout_set.exercise_id,
        weight=workout_set.weight,
        reps=workout_set.reps,
        set_order=workout_set.set_order,
    )

    db.add(db_workout_set)
    db.commit()
    db.refresh(db_workout_set)

    return db_workout_set


@router.delete("/workout-sets/{set_id}")
def delete_workout_set(
    set_id: int,
    db: Session = Depends(get_db),
):
    db_workout_set = db.query(models.WorkoutSet).get(set_id)

    if not db_workout_set:
        return {"message": "Not found"}

    db.delete(db_workout_set)
    db.commit()

    return {"message": "deleted"}
