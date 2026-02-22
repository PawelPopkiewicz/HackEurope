# ANTIGRAVITY — Pen Test Agent

An AI-powered suite of agents for automated security monitoring, vulnerability discovery, and remediation.

## Overview

ANTIGRAVITY monitors honeypot activity, classifies threats using MITRE ATT&CK, and automatically generates code fixes for discovered vulnerabilities.

```
SSH attack → Cowrie honeypot logs → Classification Agent → Fixer Agent → PR with patch
```

## Architecture

- **Frontend** — React + Vite dashboard with real-time SSE updates
- **Backend** — FastAPI server with modular agent pipeline
- **Agents** — LangGraph-based agents for log classification and automated fixing
- **Honeypot** — Cowrie SSH honeypot configuration

## Quick Start

### Backend

```bash
pip install -r requirements.txt
python -m backend.main
```

The API will be available at `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The dashboard will be available at `http://localhost:5173`.

### Docker

```bash
docker-compose up
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Service health check |
| GET | `/api/v1/logs/stream` | Real-time Cowrie log stream (SSE) |
| GET | `/api/v1/classification/stream` | Threat classification stream (SSE) |
| GET | `/api/v1/fixing/stream` | Automated fix stream (SSE) |
| GET | `/api/v1/dashboard/stream` | Consolidated dashboard stream (SSE) |
| POST | `/api/v1/dashboard/send_honeypot_json` | Push honeypot JSON data |
