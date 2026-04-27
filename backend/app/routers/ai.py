import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
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
    prompt = _build_prompt(db_exercise.name, summary, history, request.goal)
    analysis, selected_model = generate_text(prompt, request.model)
    analysis = _normalize_analysis_text(analysis)

    return {
        "exercise_id": exercise_id,
        "exercise_name": db_exercise.name,
        "model": selected_model,
        "history_count": len(history),
        "summary": summary,
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


def _normalize_analysis_text(analysis: str) -> str:
    return analysis.replace("リップ", "レップ")


def _build_prompt(
    exercise_name: str,
    summary: dict,
    history: list[dict],
    goal: str | None,
) -> str:
    recent_history = history[-20:]

    return f"""
あなたは筋力トレーニングの記録を分析するコーチです。
以下の記録をもとに、日本語で短く実用的に分析してください。

出力形式:
1. 現状の評価
2. 次回の重量・回数の提案
3. 注意点

種目: {exercise_name}
目標: {goal or "指定なし"}
サマリー:
{json.dumps(summary, ensure_ascii=False)}

直近履歴:
{json.dumps(recent_history, ensure_ascii=False)}

注意:
- 医療的な診断はしない
- 無理な増量を勧めない
- 次回重量の増加は原則2.5kg以内にする
- 「リップ」ではなく「レップ」と書く
- volumeは「総ボリューム」と表現する
- データが少ない場合は、その前提を明記する
""".strip()
