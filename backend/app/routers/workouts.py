from fastapi import APIRouter, Depends, HTTPException
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
    db_workout = db.get(models.Workout, workout_id)

    if not db_workout:
        raise HTTPException(status_code=404, detail="Workout not found")

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


@router.delete("/workouts/{workout_id}")
def delete_workout(
    workout_id: int,
    db: Session = Depends(get_db),
):
    db_workout = db.get(models.Workout, workout_id)

    if not db_workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    db.delete(db_workout)
    db.commit()

    return {"message": "deleted"}


@router.get(
    "/workouts/{workout_id}/sets",
    response_model=list[schemas.WorkoutSetResponse],
)
def get_workout_sets(
    workout_id: int,
    db: Session = Depends(get_db),
):
    db_workout = db.get(models.Workout, workout_id)

    if not db_workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    return (
        db.query(models.WorkoutSet)
        .filter(models.WorkoutSet.workout_id == workout_id)
        .order_by(models.WorkoutSet.set_order.asc())
        .all()
    )


@router.post("/workouts/{workout_id}/sets", response_model=schemas.WorkoutSetResponse)
def create_workout_set(
    workout_id: int,
    workout_set: schemas.WorkoutSetCreate,
    db: Session = Depends(get_db),
):
    db_workout = db.get(models.Workout, workout_id)

    if not db_workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    db_exercise = db.get(models.Exercise, workout_set.exercise_id)

    if not db_exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

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


@router.put("/workout-sets/{set_id}", response_model=schemas.WorkoutSetResponse)
def update_workout_set(
    set_id: int,
    workout_set: schemas.WorkoutSetUpdate,
    db: Session = Depends(get_db),
):
    db_workout_set = db.get(models.WorkoutSet, set_id)

    if not db_workout_set:
        raise HTTPException(status_code=404, detail="Workout set not found")

    db_exercise = db.get(models.Exercise, workout_set.exercise_id)

    if not db_exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    db_workout_set.exercise_id = workout_set.exercise_id
    db_workout_set.weight = workout_set.weight
    db_workout_set.reps = workout_set.reps
    db_workout_set.set_order = workout_set.set_order

    db.commit()
    db.refresh(db_workout_set)

    return db_workout_set


@router.delete("/workout-sets/{set_id}")
def delete_workout_set(
    set_id: int,
    db: Session = Depends(get_db),
):
    db_workout_set = db.get(models.WorkoutSet, set_id)

    if not db_workout_set:
        raise HTTPException(status_code=404, detail="Workout set not found")

    db.delete(db_workout_set)
    db.commit()

    return {"message": "deleted"}
