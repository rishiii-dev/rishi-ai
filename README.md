# Rishi AI

A private, self-hosted local AI assistant for a headless Linux machine. It runs a Qwen3 4B model with Ollama, exposes a small FastAPI service, and provides a custom web chat UI that devices on the same LAN can open in a browser.

## Architecture

```text
Browser / VM on LAN
        |
        | HTTP :8080
        v
+-------------------+
| FastAPI backend   |
| Rishi AI web app  |
+---------+---------+
          |
          | Docker network
          v
+-------------------+
| Ollama            |
| qwen3:4b          |
+-------------------+
```

## Features

- Headless/server-friendly deployment.
- Local inference through Ollama.
- Qwen3 4B default model.
- Custom Rishi AI identity and `Welcome Rishi!` greeting behavior.
- Browser UI served by FastAPI.
- LAN access through one port (`8080`).
- Health endpoint at `/api/health`.
- No cloud API key is required for inference.

## Requirements

- Linux server/VM
- Docker Engine + Docker Compose plugin
- Enough RAM/CPU for a 4B local model; GPU is optional
- Network access for the initial container/model download

## Start on a Linux TTY

```bash
git clone <your-repository-url> rishi-ai
cd rishi-ai
./scripts/setup.sh
```

Then open:

```text
http://localhost:8080
```

From another machine on the same LAN, use the server's LAN IP:

```text
http://SERVER_IP:8080
```

Find the server IP with:

```bash
hostname -I
```

## Useful commands

```bash
docker compose ps
docker compose logs -f backend
docker compose logs -f ollama
docker compose restart
```

Check the API directly:

```bash
curl http://localhost:8080/api/health
```

## Customization

The system prompt is in `backend/app.py`. The UI is in `frontend/index.html`. Change `OLLAMA_MODEL` in `docker-compose.yml` to use another Ollama model.

## Security note

This first version is designed for a trusted local network. It does **not** include authentication, HTTPS, rate limiting, or internet exposure controls. Do not port-forward it to the public internet as-is.

## License

MIT
