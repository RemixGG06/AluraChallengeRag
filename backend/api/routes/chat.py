"""Ruta /api/chat — conversación con el agente MentorTI Nexus."""

from __future__ import annotations

from pydantic import BaseModel, Field
from fastapi import APIRouter

from backend.common.cache import response_cache

router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    history: list[ChatMessage] = Field(default_factory=list)
    lang: str = Field(default="es", pattern="^(es|pt)$")


class ChatResponse(BaseModel):
    answer: str
    source_type: str
    sources: list[dict]
    model: str


@router.post("", response_model=ChatResponse)
def send_message(req: ChatRequest):
    from backend.llm.agent import ask

    cached = response_cache.get(req.question, req.lang)
    if cached is not None:
        return ChatResponse(**cached)

    chat_history = [{"role": m.role, "content": m.content} for m in req.history[-10:]]
    result = ask(req.question, chat_history=chat_history)

    response = ChatResponse(
        answer=result.get("answer", ""),
        source_type=result.get("source_type", "none"),
        sources=result.get("sources", []),
        model=result.get("model", ""),
    )
    response_cache.set(req.question, req.lang, response.model_dump())
    return response
