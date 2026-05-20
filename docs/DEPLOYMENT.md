# Deployment Guide

This project is designed for a small VPS deployment using Python, systemd, Nginx, and Certbot.

## 1. Create Runtime Environment

```bash
cd /root/chatbot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Configure Environment

Create `/root/chatbot/chatbot.env`:

```bash
ANTHROPIC_API_KEY=your_key_here
FRONTEND_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

Keep this file on the server only. Do not commit it.

## 3. Install systemd Service

```bash
cp /root/chatbot/chatbot-api.service /etc/systemd/system/chatbot-api.service
systemctl daemon-reload
systemctl enable chatbot-api
systemctl start chatbot-api
systemctl status chatbot-api
```

The service runs:

```text
127.0.0.1:8002
```

## 4. Configure Nginx

For the current shared API domain:

```bash
cp /root/chatbot/api.example.com.nginx /etc/nginx/sites-available/your-api-domain.com
ln -s /etc/nginx/sites-available/your-api-domain.com /etc/nginx/sites-enabled/your-api-domain.com
nginx -t
systemctl reload nginx
```

The active route is:

```text
https://your-api-domain.com/chatbot/
```

For a dedicated chatbot subdomain, use `chatbot.nginx` and update DNS before running Certbot.

## 5. TLS

```bash
certbot --nginx -d your-api-domain.com
nginx -t
systemctl reload nginx
```

## 6. Verify

Local:

```bash
curl http://127.0.0.1:8002/health
```

Public:

```bash
curl https://your-api-domain.com/chatbot/health
```

Streaming chat:

```bash
curl -N https://your-api-domain.com/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Give me a concise portfolio summary."}]}'
```

## 7. Operational Notes

- Restart after code or prompt changes: `systemctl restart chatbot-api`.
- Logs: `journalctl -u chatbot-api -f`.
- Nginx test before reload: `nginx -t`.
- Keep `chatbot.env` readable only by trusted server users.
