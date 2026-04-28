import json

from .. import models


def build_exercise_analysis_prompt(
    exercise_name: str,
    summary: dict,
    history: list[dict],
    goal: str | None,
) -> str:
    recent_history = history[-20:]

    return f"""
You are a practical strength training coach.
Analyze the exercise log below and respond in Japanese.

Return valid JSON only. Do not wrap it in markdown.
Use this exact shape:
{{
  "summary": "具体的な現状評価を日本語で書く",
  "recommendation": "具体的な次回提案を日本語で書く",
  "cautions": ["具体的な注意点を日本語で書く"]
}}

Rules:
- Do not copy the example text.
- Do not make medical diagnoses.
- Do not recommend aggressive weight increases.
- Weight increases should usually be 2.5kg or less.
- Write natural Japanese.
- Avoid awkward katakana translations.
- Use レップ, not リップ.
- Translate volume as 総ボリューム.
- If there is little data, mention that clearly.

Exercise: {exercise_name}
Goal: {goal or "指定なし"}
Metrics:
{json.dumps(summary, ensure_ascii=False)}

Recent history:
{json.dumps(recent_history, ensure_ascii=False)}
""".strip()


def build_workout_analysis_prompt(
    workout: models.Workout,
    sets: list[dict],
    total_volume: float,
    goal: str | None,
) -> str:
    return f"""
You are a practical strength training coach.
Analyze the workout log below and respond in Japanese.

Return valid JSON only. Do not wrap it in markdown.
Use this exact shape:
{{
  "summary": "具体的なワークアウト全体の評価を日本語で書く",
  "recommendation": "具体的な次回メニューや強度の提案を日本語で書く",
  "cautions": ["具体的な注意点を日本語で書く"]
}}

Rules:
- Do not copy the example text.
- Do not make medical diagnoses.
- Do not recommend aggressive weight increases.
- Weight increases should usually be 2.5kg or less.
- Write natural Japanese.
- Avoid awkward katakana translations.
- Use レップ, not リップ.
- Translate volume as 総ボリューム.
- If there is little data, mention that clearly.

Workout date: {workout.trained_at.isoformat()}
Note: {workout.note or "なし"}
Goal: {goal or "指定なし"}
Set count: {len(sets)}
Total volume: {total_volume}

Sets:
{json.dumps(sets, ensure_ascii=False)}
""".strip()
