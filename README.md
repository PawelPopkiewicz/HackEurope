# ANTIGRAVITY — Pen Test Agent

An AI-powered security platform that automates vulnerability discovery and remediation using honeypots and intelligent agents.

## Architecture

1. **Honeypot (Cowrie)** — Captures attacker SSH sessions and produces structured JSON logs.
2. **Backend (FastAPI)** — Monitors log changes, classifies threats using MITRE ATT&CK, and streams events to connected clients via Server-Sent Events (SSE).
3. **Frontend (React + Vite)** — Real-time dashboard for viewing live honeypot logs, threat classifications, and automated fix suggestions.

## Agents

- **Classification Agent** — Maps honeypot events to MITRE ATT&CK techniques and assigns severity scores.
- **Fixer Agent** — Generates pull requests to remediate identified vulnerabilities.

## Quick Start

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the backend
python -m backend.main

# Start the frontend (in a separate terminal)
cd frontend
npm install
npm run dev
```

## Docker

```bash
docker-compose up
```

## API

| Endpoint | Description |
|---|---|
| `GET /` | Service status |
| `GET /api/v1/health` | Health check |
| `GET /api/v1/dashboard/stream` | SSE stream for all dashboard events |
| `POST /api/v1/dashboard/send_honeypot_json` | Push honeypot log data |
| `GET /api/v1/logs/stream` | SSE stream for raw Cowrie logs |
