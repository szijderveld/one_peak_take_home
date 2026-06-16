import json
from collections.abc import AsyncIterator

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.agent.research_agent import ResearchAgent
from app.config import get_settings
from app.enrichment.enricher import enrich
from app.models.domain import Space
from app.pipeline import cleaning
from app.pipeline.pipeline import build_landscape
from app.pipeline.pulse_client import PulseError

app = FastAPI(title="PULSE Competitive Landscape")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


class LandscapeRequest(BaseModel):
    domain: str


@app.post("/api/landscape", response_model=Space)
async def landscape(req: LandscapeRequest) -> Space:
    settings = get_settings()
    domain = cleaning.clean_domain(req.domain) or req.domain
    try:
        space = await build_landscape(domain, settings)
    except PulseError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    await enrich(space, settings)  # fills AI properties in place; no-op without a key
    return space


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    space: Space  # the landscape the user is looking at (sent from the client)
    messages: list[ChatMessage]


@app.post("/api/chat")
async def chat(req: ChatRequest) -> StreamingResponse:
    settings = get_settings()
    if not settings.ai_enabled:
        raise HTTPException(status_code=503, detail="Chat needs an ANTHROPIC_API_KEY.")
    agent = ResearchAgent(settings, req.space)
    history = [m.model_dump() for m in req.messages]

    async def events() -> AsyncIterator[str]:
        try:
            async for delta in agent.stream(history):
                yield f"data: {json.dumps({'delta': delta})}\n\n"
        except Exception as exc:  # surface errors to the client stream
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"
        yield "data: {\"done\": true}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")
