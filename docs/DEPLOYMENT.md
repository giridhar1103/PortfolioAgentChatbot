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
FRONTEND_ORIGINS=https://giriworks.com,https://www.giriworks.com
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
cp /root/chatbot/api.giriworks.com.nginx /etc/nginx/sites-available/api.giriworks.com
ln -s /etc/nginx/sites-available/api.giriworks.com /etc/nginx/sites-enabled/api.giriworks.com
nginx -t
systemctl reload nginx
```

The active route is:

```text
https://api.giriworks.com/chatbot/
```

For a dedicated chatbot subdomain, use `chatbot.nginx` and update DNS before running Certbot.

## 5. TLS

```bash
certbot --nginx -d api.giriworks.com
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
curl https://api.giriworks.com/chatbot/health
```

Streaming chat:

```bash
curl -N https://api.giriworks.com/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Give me a concise summary of Giridhar."}]}'
```

## 7. Operational Notes

- Restart after code or prompt changes: `systemctl restart chatbot-api`.
- Logs: `journalctl -u chatbot-api -f`.
- Nginx test before reload: `nginx -t`.
- Keep `chatbot.env` readable only by trusted server users.
