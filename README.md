# ANTIGRAVITY 🛡️

**ANTIGRAVITY** is an AI-powered honeypot monitoring and threat response platform built at HackEurope.

It deploys a [Cowrie](https://github.com/cowrie/cowrie) SSH honeypot to attract attackers, then automatically classifies threats using a MITRE ATT&CK–based agent and suggests remediation steps via an LLM-powered fixer agent.

## Architecture

```
Cowrie SSH Honeypot  →  Backend (FastAPI)  →  Frontend (React)
       ↓                      ↓
   JSON logs          Classification Agent
                       (MITRE ATT&CK)
                             ↓
                        Fixer Agent
                         (LLM/Gemini)
```

1. The Cowrie honeypot captures SSH intrusion attempts and writes them to a JSON log file.
2. The FastAPI backend monitors the log file and streams events to the frontend via Server-Sent Events (SSE).
3. The Classification Agent maps attacker behaviour to MITRE ATT&CK tactics and techniques.
4. The Fixer Agent proposes automated remediation actions.

## Getting Started

### Prerequisites

- Docker & Docker Compose
- A `GOOGLE_API_KEY` for the LLM fixer agent

### Running with Docker Compose

```bash
# Copy and configure environment variables
cp .env.example .env   # then edit .env with your GOOGLE_API_KEY

# Start all services
docker compose up --build
```

- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:5173 (when running `npm run dev` inside `frontend/`)

### Running the frontend locally

```bash
cd frontend
npm install
npm run dev
```

### Running the backend locally

```bash
pip install -r requirements.txt
python -m backend.main
```

## Project Structure

```
├── backend/          # FastAPI backend
│   ├── agents/       # Classification & fixer agents
│   ├── api/          # SSE endpoints (logs, classification, fixer, dashboard)
│   └── core/         # Shared utilities
├── frontend/         # React + Vite frontend
│   └── src/
│       └── components/   # Dashboard UI components
├── cowrie_config/    # Cowrie honeypot configuration
├── llm/              # LLM prompt templates
├── scripts/          # Helper scripts
└── docker-compose.yml
```

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /api/v1/logs/stream` | Stream raw honeypot log events |
| `GET /api/v1/classification/stream` | Stream MITRE-classified threat events |
| `GET /api/v1/fixing/stream` | Stream AI remediation suggestions |
| `GET /api/v1/dashboard` | Aggregated dashboard data |
