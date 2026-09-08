import os
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:4b")
RISHI_NAME = os.getenv("RISHI_NAME", "Rishi")
FRONTEND_DIR = Path("/app/frontend")

SYSTEM_PROMPT = f"""You are Rishi AI, a private self-hosted local assistant owned by {RISHI_NAME}.
Be helpful, concise, and honest. Do not claim to have internet access unless it is explicitly provided.
At the beginning of every brand-new conversation, greet the user with exactly: Welcome {RISHI_NAME}!
After that greeting, answer the user's request normally.
"""

app = FastAPI(title="Rishi AI", version="1.0.0")

class Message(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=12000)

class ChatRequest(BaseModel):
    messages: list[Message] = Field(min_length=1, max_length=40)

@app.get("/api/health")
async def health() -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            r.raise_for_status()
            models = r.json().get("models", [])
        return {"status": "ok", "model": OLLAMA_MODEL, "ollama": "ok", "models": [m.get("name") for m in models]}
    except Exception as exc:
        return {"status": "degraded", "model": OLLAMA_MODEL, "ollama": "unavailable", "error": str(exc)}

@app.post("/api/chat")
async def chat(payload: ChatRequest) -> dict[str, str]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(m.model_dump() for m in payload.messages)
    try:
        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json={"model": OLLAMA_MODEL, "messages": messages, "stream": False},
            )
            response.raise_for_status()
            data = response.json()
        content = data.get("message", {}).get("content", "")
        if not content:
            raise HTTPException(status_code=502, detail="Model returned an empty response")
        return {"content": content, "model": OLLAMA_MODEL}
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text[:500]
        raise HTTPException(status_code=502, detail=f"Ollama error: {detail}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail="Could not reach the local model server") from exc

@app.get("/api/config")
async def config() -> dict[str, str]:
    return {"name": RISHI_NAME, "model": OLLAMA_MODEL}

@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")
