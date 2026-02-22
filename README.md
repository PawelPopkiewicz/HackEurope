
# HackEurope — ANTIGRAVITY

An AI-powered honeypot monitoring and threat response platform.

## Overview

ANTIGRAVITY is a full-stack application that combines a honeypot sensor with an intelligent backend to detect, classify, and remediate cyber threats in real time.

### How it works

1. **SSH Honeypot** (via Cowrie) — captures attacker activity and produces structured JSON log files.
2. **Log Watcher** — a server-side watcher polls for new log entries every 5 minutes and forwards them to the backend pipeline.
3. **Classification Agent** — analyses incoming logs using MITRE ATT&CK techniques to identify attack patterns.
4. **Fixer Agent** — proposes automated remediation actions based on classified threats.
5. **Dashboard** — a React frontend displays live event streams, classifications, and remediation suggestions.

## Stack

- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: Python + FastAPI (SSE streams)
- **AI**: LLM-powered classification and correlation agents
- **Honeypot**: Cowrie SSH honeypot

## Getting Started

```bash
# Start all services
docker-compose up
```

The frontend is available at `http://localhost:5173` and the backend API at `http://localhost:8000`.
