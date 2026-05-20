# API Reference

The chatbot exposes a small HTTP API designed for a browser chat widget. The chat endpoint returns Server-Sent Events so the frontend can render tokens as they arrive.

## Base URLs

Production:

```text
https://your-api-domain.com/chatbot
```

Local:

```text
http://127.0.0.1:8002
```

## Health

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

## Chat

```http
POST /chat
Content-Type: application/json
```

Request body:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Tell me about this person's project experience."
    }
  ]
}
```

The final message must use the `user` role. The backend trims the conversation to the most recent 20 messages before calling the model.

Streaming response:

```text
data: {"text":"They have worked on"}
data: {"text":" cloud data pipelines..."}
data: [DONE]
```

Error event:

```text
data: {"error":"..."}
```

## Frontend Integration Notes

Use `fetch` with `ReadableStream`. Do not use `EventSource`, since the request is a `POST`.

```ts
const response = await fetch("https://your-api-domain.com/chatbot/chat", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ messages }),
});

const reader = response.body?.getReader();
const decoder = new TextDecoder();

while (reader) {
  const { done, value } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value, { stream: true });
  for (const line of chunk.split("\n")) {
    if (!line.startsWith("data: ")) continue;
    const payload = line.slice(6).trim();
    if (payload === "[DONE]") break;

    const event = JSON.parse(payload);
    if (event.text) {
      // Append event.text to the active assistant message.
    }
  }
}
```
