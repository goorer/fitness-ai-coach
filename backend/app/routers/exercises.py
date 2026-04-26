from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/exercises", tags=["Exercises"])


@router.post("", response_model=schemas.ExerciseResponse)
def create_exercise(
    exercise: schemas.ExerciseCreate,
    db: Session = Depends(get_db),
):
    db_exercise = models.Exercise(
        name=exercise.name,
        body_part=exercise.body_part,
    )

    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)

    return db_exercise

@router.get("", response_model=list[schemas.ExerciseResponse])
def get_exercises(db: Session = Depends(get_db)):
    return db.query(models.Exercise).all()

@router.put("/{exercise_id}", response_model=schemas.ExerciseResponse)
def update_exercise(
    exercise_id: int,
    exercise: schemas.ExerciseCreate,
    db: Session = Depends(get_db),
):
    db_exercise = db.query(models.Exercise).get(exercise_id)

    if not db_exercise:
        return None

    db_exercise.name = exercise.name
    db_exercise.body_part = exercise.body_part

    db.commit()
    db.refresh(db_exercise)

    return db_exercise

@router.delete("/{exercise_id}")
def delete_exercise(
    exercise_id: int,
    db: Session = Depends(get_db),
):
    db_exercise = db.query(models.Exercise).get(exercise_id)

    if not db_exercise:
        return {"message": "Not found"}

    db.delete(db_exercise)
    db.commit()

    return {"message": "deleted"}