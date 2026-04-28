from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services.ai_prompts import (
    build_exercise_analysis_prompt,
    build_workout_analysis_prompt,
)
from ..services.ai_response import normalize_analysis_text, parse_analysis_sections
from ..services.llm import generate_text

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post(
    "/analyze-exercise/{exercise_id}",
    response_model=schemas.AIExerciseAnalysisResponse,
)
def analyze_exercise(
    exercise_id: int,
    request: schemas.AIExerciseAnalysisRequest,
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

    history = [
        {
            "trained_at": workout.trained_at.isoformat(),
            "weight": workout_set.weight,
            "reps": workout_set.reps,
            "set_order": workout_set.set_order,
            "volume": workout_set.weight * workout_set.reps,
        }
        for workout_set, workout in rows
    ]

    summary = _build_summary(exercise_id, history)
    prompt = build_exercise_analysis_prompt(
        db_exercise.name,
        summary,
        history,
        request.goal,
    )
    analysis, selected_model = generate_text(prompt, request.model)
    analysis = normalize_analysis_text(analysis)
    sections = parse_analysis_sections(analysis)

    return {
        "exercise_id": exercise_id,
        "exercise_name": db_exercise.name,
        "model": selected_model,
        "history_count": len(history),
        "metrics": summary,
        "summary": sections["summary"],
        "recommendation": sections["recommendation"],
        "cautions": sections["cautions"],
        "analysis": analysis,
    }


@router.post(
    "/analyze-workout/{workout_id}",
    response_model=schemas.AIWorkoutAnalysisResponse,
)
def analyze_workout(
    workout_id: int,
    request: schemas.AIWorkoutAnalysisRequest,
    db: Session = Depends(get_db),
):
    db_workout = db.get(models.Workout, workout_id)

    if not db_workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    rows = (
        db.query(models.WorkoutSet, models.Exercise)
        .join(models.Exercise, models.WorkoutSet.exercise_id == models.Exercise.id)
        .filter(models.WorkoutSet.workout_id == workout_id)
        .order_by(models.WorkoutSet.set_order.asc())
        .all()
    )

    sets = [
        {
            "exercise_id": workout_set.exercise_id,
            "exercise_name": exercise.name,
            "weight": workout_set.weight,
            "reps": workout_set.reps,
            "set_order": workout_set.set_order,
            "volume": workout_set.weight * workout_set.reps,
        }
        for workout_set, exercise in rows
    ]
    total_volume = sum(item["volume"] for item in sets)

    prompt = build_workout_analysis_prompt(
        db_workout,
        sets,
        total_volume,
        request.goal,
    )
    analysis, selected_model = generate_text(prompt, request.model)
    analysis = normalize_analysis_text(analysis)
    sections = parse_analysis_sections(analysis)

    return {
        "workout_id": workout_id,
        "model": selected_model,
        "set_count": len(sets),
        "total_volume": total_volume,
        "summary": sections["summary"],
        "recommendation": sections["recommendation"],
        "cautions": sections["cautions"],
        "analysis": analysis,
    }


def _build_summary(exercise_id: int, history: list[dict]) -> dict:
    if not history:
        return {
            "exercise_id": exercise_id,
            "total_sets": 0,
            "max_weight": None,
            "max_reps": None,
            "total_volume": 0,
            "suggested_next_weight": None,
        }

    max_weight = max(item["weight"] for item in history)
    max_reps = max(item["reps"] for item in history)
    total_volume = sum(item["volume"] for item in history)

    return {
        "exercise_id": exercise_id,
        "total_sets": len(history),
        "max_weight": max_weight,
        "max_reps": max_reps,
        "total_volume": total_volume,
        "suggested_next_weight": max_weight + 2.5,
    }
