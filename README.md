
# ANTIGRAVITY

A honeypot monitoring and AI-powered remediation platform.

## Overview

ANTIGRAVITY captures SSH intrusion attempts via [Cowrie](https://github.com/cowrie/cowrie), streams the logs in real-time, classifies threats automatically, and suggests or applies fixes using an AI agent pipeline.

## Architecture

```
ssh → Cowrie → JSON logs → Backend (FastAPI SSE) → Frontend (React)
                                     ↓
                           Classification Agent
                                     ↓
                              Fixer Agent
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker (optional, for Cowrie honeypot)

### Backend

```bash
pip install -r requirements.txt
python -m backend.main
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The UI will be available at `http://localhost:5173`.

### Docker (full stack)

```bash
docker-compose up
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/logs/stream` | SSE stream of Cowrie honeypot logs |
| GET | `/api/v1/classification/stream` | SSE stream of threat classifications |
| GET | `/api/v1/fixing/stream` | SSE stream of automated fix suggestions |

## Project Structure

```
backend/      FastAPI application (agents, API routes, core utilities)
frontend/     React + Vite UI dashboard
cowrie_config/ Cowrie honeypot configuration
llm/          LLM agent definitions
scripts/      Helper scripts
data/         Log data directory
```
