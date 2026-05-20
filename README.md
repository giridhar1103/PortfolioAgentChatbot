# Portfolio Agent Chatbot

A production-ready portfolio assistant template for a personal website. It is built as a lean FastAPI service that streams Claude responses into a frontend chat widget and keeps the conversation focused on professional background, projects, skills, recruiting questions, and job-description fit.

This is not a generic chat demo. It is a focused portfolio interface: a recruiter can ask about experience, paste a job description, or explore project depth, and the assistant responds with grounded answers from a curated system profile.

## What It Does

- Streams responses over Server-Sent Events for a smooth chat experience.
- Uses a portfolio-specific system prompt with education, experience, projects, skills, contact context, and JD fit instructions.
- Detects job descriptions and turns them into structured fit analysis.
- Keeps a strict topic boundary so the assistant stays focused on the portfolio owner's professional profile.
- Trims conversation history to control context size.
- Runs behind Nginx with TLS, rate limiting, and systemd process supervision.

## Why This Project Matters

The goal is to make a personal portfolio feel interactive without turning it into a gimmick. The assistant acts like a guided technical resume: concise for casual visitors, deeper for recruiters, and practical when someone brings a real job description.

It shows production habits that matter on a resume:

- API design with FastAPI and Pydantic.
- Streaming UX through SSE.
- LLM integration with a controlled system prompt.
- Deployment on a VPS with systemd and Nginx.
- CORS, request limits, health checks, and environment-based secrets.

## Architecture

```text
Portfolio frontend
  |
  | POST /chat with conversation history
  v
Nginx reverse proxy
  |
  | public: https://your-api-domain.com/chatbot/
  | local:  http://127.0.0.1:8002/
  v
FastAPI chatbot service
  |
  | Anthropic Messages API stream
  v
Claude Haiku
```

## API

Health check:

```bash
curl https://your-api-domain.com/chatbot/health
```

Chat request:

```bash
curl -N https://your-api-domain.com/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"What kind of projects has this person built?"}]}'
```

Response format:

```text
data: {"text":"They have built"}
data: {"text":" production-grade data systems..."}
data: [DONE]
```

## Local Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `ANTHROPIC_API_KEY` in `.env`, then run:

```bash
export $(grep -v '^#' .env | xargs)
uvicorn app:app --host 127.0.0.1 --port 8002 --reload
```

Open:

```text
http://127.0.0.1:8002/health
```

## Environment Variables

| Variable | Purpose |
| --- | --- |
| `ANTHROPIC_API_KEY` | Anthropic API key used by the backend. |
| `FRONTEND_ORIGINS` | Comma-separated list of allowed browser origins for CORS. |

## Repository Map

```text
.
├── app.py
├── system_prompt.py
├── requirements.txt
├── chatbot-api.service
├── chatbot.nginx
├── api.example.com.nginx
├── .env.example
└── docs/
    ├── API.md
    ├── ARCHITECTURE.md
    └── DEPLOYMENT.md
```
