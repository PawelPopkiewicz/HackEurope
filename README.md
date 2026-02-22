# ANTIGRAVITY — Pen Test Agent

An AI-powered suite of agents for automated security monitoring and vulnerability remediation.

## Overview

- **Honeypot Monitoring** — Cowrie SSH honeypot captures attacker activity and emits structured JSON logs.
- **Classification Agent** — Ingests honeypot logs via SSE, classifies threats in real-time, and matches against known attack rules.
- **Fixer Agent** — Generates pull requests to automatically remediate discovered vulnerabilities.

## Architecture

```
Honeypot (Cowrie SSH)
  └── logs.json (updated on new activity)
        └── Backend (FastAPI + SSE)
              ├── /api/v1/logs/stream
              ├── /api/v1/classification/stream
              └── /api/v1/fixing/stream
                    └── Frontend (React + Vite)
```

## Getting Started

```bash
# Start all services
docker-compose up

# Or run the backend manually
pip install -r requirements.txt
python -m backend.main

# Run the frontend
cd frontend && npm install && npm run dev
```

## Stack

- **Backend**: Python, FastAPI, SSE
- **Frontend**: React, Vite, Tailwind CSS, ReactFlow
- **Honeypot**: Cowrie
