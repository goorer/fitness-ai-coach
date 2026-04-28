import os

from fastapi import HTTPException
from langchain_ollama import ChatOllama


OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


def generate_text(prompt: str, model: str | None = None) -> tuple[str, str]:
    selected_model = (model or OLLAMA_MODEL).strip()

    if selected_model == "string":
        selected_model = OLLAMA_MODEL

    try:
        llm = ChatOllama(
            model=selected_model,
            base_url=OLLAMA_BASE_URL,
            temperature=0,
        )
        response = llm.invoke(prompt)
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"LLM service unavailable: {error}",
        ) from error

    content = response.content

    if isinstance(content, str):
        return content, selected_model

    return str(content), selected_model
