
# HackEurope — ANTIGRAVITY

An AI-powered honeypot monitoring and penetration testing platform built for HackEurope.

## Overview

ANTIGRAVITY combines a honeypot, real-time threat classification, and an AI fixer agent into a single dashboard.

- **Honeypot**: An SSH honeypot (powered by Cowrie) captures attacker activity and writes structured logs to a JSON file.
- **Classification Agent**: The backend monitors the log file every 5 minutes. When new events are detected, they are streamed via SSE to the Classification Agent, which applies threat-intelligence rules to categorise each attack.
- **Fixer Agent**: Identified vulnerabilities are passed to an LLM-backed Fixer Agent that generates pull-request-ready remediation code.

## Architecture

```
Attacker → SSH Honeypot (Cowrie) → logs.json
                                        ↓
                          FastAPI Backend (SSE streaming)
                          ┌─────────────┬──────────────┐
                    Classification    Fixer         Dashboard
                       Agent          Agent          API
                          └─────────────┴──────────────┘
                                        ↓
                            React Frontend (Vite + Tailwind)
```

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Node.js ≥ 18
- Python ≥ 3.11

### Run with Docker Compose

```bash
docker-compose up --build
```

### Run locally

```bash
# Backend
pip install -r requirements.txt
uvicorn backend.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

The frontend is served at `http://localhost:5173` and the API at `http://localhost:8000`.
