import os

import requests
from fastapi import HTTPException


OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


def generate_text(prompt: str, model: str | None = None) -> tuple[str, str]:
    selected_model = (model or OLLAMA_MODEL).strip()

    if selected_model == "string":
        selected_model = OLLAMA_MODEL

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": selected_model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=180,
        )
    except requests.RequestException as error:
        raise HTTPException(
            status_code=503,
            detail=f"LLM service unavailable: {error}",
        ) from error

    if response.status_code >= 400:
        raise HTTPException(
            status_code=503,
            detail=f"LLM service error: {response.text}",
        )

    data = response.json()
    return data.get("response", ""), selected_model
