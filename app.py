from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import anthropic
import os
import json

from system_prompt import SYSTEM_PROMPT

app = FastAPI(
    title="Portfolio Agent Chatbot",
    description="Streaming portfolio assistant for recruiter and project-fit conversations.",
    version="1.0.0",
)

origins = os.environ.get("FRONTEND_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS", "GET"],
    allow_headers=["Content-Type"],
)

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 1024
MAX_MESSAGES = 20  # prevent context bloat


def _clean_stream_text(text: str) -> str:
    return text.replace("\u2014", "-").replace("\u2013", "-").replace("*", "")


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


def _validate_messages(messages: list[Message]) -> list[dict]:
    if not messages:
        raise HTTPException(status_code=400, detail="messages cannot be empty")
    if messages[-1].role != "user":
        raise HTTPException(status_code=400, detail="last message must be from user")
    # trim to last N messages to cap context size
    trimmed = messages[-MAX_MESSAGES:]
    return [{"role": m.role, "content": m.content} for m in trimmed]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {
        "name": "Portfolio Agent Chatbot",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


@app.post("/chat")
async def chat(req: ChatRequest):
    msgs = _validate_messages(req.messages)

    def generate():
        try:
            with client.messages.stream(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=[
                    {
                        "type": "text",
                        "text": SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                messages=msgs,
            ) as stream:
                for text in stream.text_stream:
                    clean_text = _clean_stream_text(text)
                    if clean_text:
                        yield f"data: {json.dumps({'text': clean_text})}\n\n"
            yield "data: [DONE]\n\n"
        except anthropic.APIError as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disables nginx buffering for SSE
        },
    )
