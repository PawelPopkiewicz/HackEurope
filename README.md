# ANTIGRAVITY — Honeypot Monitoring & AI Remediation Platform

A modular backend and frontend platform for honeypot monitoring, threat classification, and AI-driven remediation.

## Architecture Overview

- **SSH Honeypot** – Captures attacker activity and produces a `.json` log file with all session events.
- **Log Watcher** – A server running on the honeypot polls every 5 minutes for changes to `logs.json`. When a change is detected, it forwards the data to the backend agent.
- **Backend Agent** – A FastAPI service that receives log data, runs MITRE ATT&CK classification, correlates multi-stage attacks, and streams results to connected dashboards via Server-Sent Events (SSE).
- **Frontend Dashboard** – A React/Vite application providing real-time visibility into classifications, fixer actions, and honeypot configuration.

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (optional, for full stack)

### Running with Docker Compose
```bash
docker-compose up --build
```

### Running the Backend Manually
```bash
pip install -r requirements.txt
python -m backend.main
```
The API will be available at `http://localhost:8000`. Visit `/api/v1/dashboard/stream` for the live SSE feed.

### Running the Frontend Manually
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Service status and available endpoints |
| GET | `/health` | Health check |
| POST | `/api/v1/dashboard/send_honeypot_json` | Ingest honeypot log data |
| GET | `/api/v1/dashboard/stream` | SSE stream of all dashboard events |
| GET | `/api/v1/logs/stream` | SSE stream of raw log events |
| GET | `/api/v1/classification/stream` | SSE stream of classification results |
| GET | `/api/v1/fixing/stream` | SSE stream of fixer agent output |
