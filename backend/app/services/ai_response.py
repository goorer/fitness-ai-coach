import json


DEFAULT_CAUTION = "AIの提案は参考情報として扱い、体調やフォームを優先してください。"


def normalize_analysis_text(analysis: str) -> str:
    return analysis.replace("リップ", "レップ").strip()


def parse_analysis_sections(analysis: str) -> dict:
    json_text = _extract_json_text(analysis)

    try:
        data = json.loads(json_text)
    except json.JSONDecodeError:
        return {
            "summary": analysis or "分析結果を取得できませんでした。",
            "recommendation": "",
            "cautions": [DEFAULT_CAUTION],
        }

    return {
        "summary": _clean_text(data.get("summary")) or "分析結果を取得できませんでした。",
        "recommendation": _clean_text(data.get("recommendation")),
        "cautions": _clean_cautions(data.get("cautions")),
    }


def _extract_json_text(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        return text

    return text[start : end + 1]


def _clean_text(value) -> str:
    if value is None:
        return ""

    return str(value).strip()


def _clean_cautions(value) -> list[str]:
    if isinstance(value, str):
        value = [value]

    if not isinstance(value, list):
        return [DEFAULT_CAUTION]

    cautions = [_clean_text(item) for item in value]
    cautions = [item for item in cautions if item]

    return cautions or [DEFAULT_CAUTION]
