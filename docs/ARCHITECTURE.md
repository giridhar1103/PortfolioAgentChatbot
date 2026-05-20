# Architecture

Portfolio Agent Chatbot is intentionally small. The main design choice is to keep orchestration simple and make the prompt, API contract, hosting path, and browser streaming behavior easy to reason about.

## Runtime Flow

```text
User opens portfolio chat widget
  |
  v
Frontend sends the full conversation history
  |
  v
FastAPI validates and trims messages
  |
  v
Anthropic Messages API streams model output
  |
  v
FastAPI converts tokens into SSE events
  |
  v
Frontend appends tokens to the assistant bubble
```

## Backend Components

| Component | Responsibility |
| --- | --- |
| `app.py` | FastAPI app, CORS, request validation, Anthropic streaming, SSE response formatting. |
| `system_prompt.py` | Portfolio knowledge base and behavior policy for the assistant. |
| `requirements.txt` | Runtime dependencies. |
| `chatbot-api.service` | systemd process definition for production. |
| `api.giriworks.com.nginx` | Active reverse-proxy shape for the shared API domain. |
| `chatbot.nginx` | Optional standalone subdomain config. |

## Behavior Policy

The assistant follows a focused behavior policy. It does not browse, call tools, or pretend to perform actions. Instead, it applies a structured decision policy inside the system prompt:

- Keep answers inside Giridhar's professional scope.
- Choose concise background summaries for broad questions.
- Switch into fit-analysis mode when a user pastes a job description.
- Match job requirements to relevant projects and experience.
- Mention real gaps without weakening the overall recruiter-facing story.
- Avoid unsupported claims.

That makes the system feel like a portfolio guide rather than an open-ended chatbot.

## Production Deployment

The live service runs as:

```text
systemd -> Uvicorn -> FastAPI -> Anthropic API
```

Nginx terminates TLS and proxies public traffic:

```text
https://api.giriworks.com/chatbot/* -> http://127.0.0.1:8002/*
```

Nginx also disables proxy buffering for the chatbot route so SSE tokens reach the browser immediately.

## Safety Boundaries

- Secrets live in `chatbot.env` on the server and are not committed.
- CORS is controlled through `FRONTEND_ORIGINS`.
- Nginx applies per-IP request and connection limits.
- The backend caps context to 20 messages.
- Off-topic questions are redirected back to portfolio and recruiting use cases.
