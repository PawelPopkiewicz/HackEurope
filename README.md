# HackEurope — Honeypot Monitoring & AI Remediation

A real-time honeypot monitoring system that collects SSH intrusion logs from [Cowrie](https://github.com/cowrie/cowrie), classifies threats using MITRE ATT&CK via an AI agent, and streams results to a React dashboard.

## Architecture

```
Cowrie Honeypot  →  Backend (FastAPI)  →  Frontend (React + Vite)
  SSH logs (JSON)     AI Classification      Real-time SSE Dashboard
```

1. **Cowrie** captures SSH session data and writes JSON logs.
2. The **FastAPI backend** ingests those logs, classifies them with a LangGraph/Gemini agent, and broadcasts events over Server-Sent Events (SSE).
3. The **React frontend** subscribes to the SSE stream and renders a live threat dashboard.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Honeypot | Cowrie |
| Backend | FastAPI, LangGraph, LangChain (Gemini), Python |
| Frontend | React 18, Vite, Tailwind CSS, React Flow |
| Infra | Docker Compose |

## Getting Started

### Prerequisites

- Docker & Docker Compose
- A `GOOGLE_API_KEY` for the Gemini AI model — obtain one at [Google AI Studio](https://aistudio.google.com/app/apikey)

### Run with Docker

```bash
cp .env.example .env   # add your GOOGLE_API_KEY
docker-compose up --build
```

- Backend API: <http://localhost:8000>
- Cowrie SSH honeypot: port `2222` / `2223`

### Run locally (development)

**Backend**

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/logs/stream` | SSE stream of raw Cowrie logs |
| `GET` | `/api/v1/classification/stream` | SSE stream of threat classifications |
| `GET` | `/api/v1/fixing/stream` | SSE stream of remediation suggestions |
| `GET` | `/api/v1/dashboard/stream` | Consolidated SSE dashboard stream |
| `POST` | `/api/v1/dashboard/send_honeypot_json` | Push honeypot JSON to the dashboard |

## Project Structure

```
.
├── backend/
│   ├── agents/          # LangGraph AI agents (MITRE classifier, etc.)
│   ├── api/             # FastAPI routers (logs, classification, fixer, dashboard)
│   ├── core/            # Shared utilities
│   └── main.py          # Application entry point
├── frontend/            # React + Vite dashboard
├── cowrie_config/       # Cowrie honeypot configuration
├── scripts/             # Helper scripts
├── docker-compose.yml
└── requirements.txt
```
