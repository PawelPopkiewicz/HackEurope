# ANTIGRAVITY

An AI-powered honeypot monitoring and threat remediation platform.

## Overview

ANTIGRAVITY continuously monitors a honeypot (powered by [Cowrie](https://github.com/cowrie/cowrie)) and uses AI agents to classify threats and suggest automated fixes.

### How it works

1. SSH connections to the honeypot produce a `.json` log file with all activity.
2. A server-side watcher checks for log changes every 5 minutes and forwards new entries to the backend agent via the API.
3. The backend agent classifies incoming logs using MITRE ATT&CK mappings and emits real-time results to connected dashboard clients via Server-Sent Events (SSE).

## Project Structure

- **`backend/`** – FastAPI backend with SSE streaming, MITRE classification agent, and honeypot configuration API.
- **`frontend/`** – React + Vite dashboard for real-time threat monitoring and honeypot configuration.
- **`llm/`** – LLM integration for threat analysis and remediation suggestions.
- **`cowrie_config/`** – Cowrie honeypot configuration files.
- **`scripts/`** – Utility scripts for deployment and log forwarding.

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker (optional, for containerised deployment)

### Running with Docker

```bash
docker-compose up --build
```

### Running locally

**Backend:**
```bash
pip install -r requirements.txt
python -m backend.main
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173` and the backend API at `http://localhost:8000`.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check |
| GET | `/api/v1/logs/stream` | SSE stream of raw Cowrie logs |
| GET | `/api/v1/dashboard/stream` | SSE stream of classified dashboard events |
| POST | `/api/v1/dashboard/send_honeypot_json` | Push honeypot log data for classification |
| GET | `/api/v1/classification/stream` | SSE stream of MITRE classification results |
| GET | `/api/v1/fixing/stream` | SSE stream of automated remediation suggestions |
