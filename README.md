
# AntiGravity — AI-Powered Honeypot Threat Intelligence Platform

AntiGravity is a cybersecurity platform that combines a **Cowrie SSH honeypot** with an **AI-powered agent pipeline** to automatically detect, classify, and remediate network intrusion attempts in real time.

When an attacker connects to the honeypot, their activity is logged, automatically classified against the [MITRE ATT&CK](https://attack.mitre.org/) framework, and fed into a LangGraph-based remediation agent that suggests and applies fixes — all streamed live to a React dashboard via Server-Sent Events (SSE).

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Development](#local-development)
  - [Docker Compose](#docker-compose)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [SSE Event Types](#sse-event-types)

---

## Features

- 🍯 **Cowrie Honeypot** — captures SSH/Telnet intrusion attempts and records attacker commands, credentials, and session data as structured JSON logs.
- 🔍 **MITRE ATT&CK Classification** — automatically maps honeypot events to MITRE ATT&CK techniques (e.g. `T1059.004 — Unix Shell`) using a Google Gemini-powered LLM.
- 🤖 **AI Remediation Agent** — a LangGraph agent pipeline analyses classified threats and generates targeted remediation steps or firewall rules.
- 📡 **Real-time Streaming** — all pipeline stages are streamed to the frontend via SSE, enabling live visualisation of active nodes in the agent graph.
- 🖥️ **React Dashboard** — a Vite + React Flow frontend that displays the live agent workflow, incoming logs, classification results, and rule suggestions.
- 🛡️ **Wazuh Integration** — optional Wazuh SIEM manager for centralised security event management.
- 📊 **Elasticsearch & Kibana** — optional ELK stack integration for long-term log storage and analytics.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Attacker                             │
└──────────────────────────┬──────────────────────────────────┘
                           │ SSH / Telnet
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Cowrie Honeypot                           │
│   Records session → writes honeypot_logs.json              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Python)                       │
│                                                             │
│  /api/v1/logs/stream ──────► Log Ingestion                 │
│  /api/v1/classification/stream ► MITRE ATT&CK Classifier   │
│  /api/v1/fixing/stream ────► LangGraph Remediation Agent   │
│                                                             │
│  All endpoints use SSE (StreamingResponse)                 │
└──────────────────────────┬──────────────────────────────────┘
                           │ SSE
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              React Frontend (Vite)                          │
│   Live agent graph · Threat feed · Rule suggestions        │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Honeypot | [Cowrie](https://github.com/cowrie/cowrie) |
| Backend | Python 3.11, FastAPI, Uvicorn |
| AI / LLM | Google Gemini (`langchain-google-genai`) |
| Agent Orchestration | [LangGraph](https://github.com/langchain-ai/langgraph) |
| Frontend | React, Vite, React Flow, Tailwind CSS |
| SIEM | Wazuh Manager |
| Log Analytics | Elasticsearch 8, Kibana 8 |
| Containerisation | Docker, Docker Compose |

---

## Project Structure

```
HackEurope/
├── backend/
│   ├── api/
│   │   ├── classification.py   # MITRE ATT&CK SSE endpoint
│   │   ├── fixer.py            # Remediation agent SSE endpoint
│   │   ├── logs.py             # Cowrie log streaming SSE endpoint
│   │   ├── router.py           # API router aggregation
│   │   └── rules.py            # Firewall rule management endpoint
│   ├── agents/                 # LangGraph agent definitions
│   ├── core/                   # Shared utilities and config
│   └── main.py                 # FastAPI app entry point
├── frontend/
│   ├── src/
│   │   ├── components/         # Layout, Sidebar, Honeypot/Rules config
│   │   ├── pages/              # Dashboard, Analytics, Settings, etc.
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── llm/
│   ├── api_call.py             # LLM utility functions
│   └── test_api.py
├── metra_classifier/
│   ├── main.py                 # MITRE ATT&CK classifier entry point
│   ├── prompts.py              # LLM prompt templates
│   └── env_setup.py
├── data/
│   ├── honeypot_logs.json      # Sample Cowrie log data
│   └── mitre_attack.json       # MITRE ATT&CK technique reference
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── SSE_README.md               # SSE integration details
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (for containerised setup)
- A [Google AI Studio](https://aistudio.google.com/) API key (for Gemini LLM)

### Local Development

#### 1. Clone the repository

```bash
git clone https://github.com/PawelPopkiewicz/HackEurope.git
cd HackEurope
```

#### 2. Backend

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`.

#### 3. Frontend

```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

The frontend will be available at `http://localhost:5173`.

### Docker Compose

The full stack (backend, Cowrie honeypot, Wazuh, Elasticsearch, Kibana) can be started with:

```bash
cp .env.example .env   # add your GOOGLE_API_KEY
docker-compose up --build
```

| Service | URL |
|---|---|
| Backend API | http://localhost:8000 |
| Kibana | http://localhost:5601 |
| Elasticsearch | http://localhost:9200 |
| Cowrie SSH (honeypot) | port 2222 |
| Wazuh API | http://localhost:55000 |

---

## Environment Variables

| Variable | Description |
|---|---|
| `GOOGLE_API_KEY` | Google Gemini API key used by the LLM classifier and remediation agent |

---

## API Endpoints

All endpoints are prefixed with `/api/v1`.

| Method | Path | Description |
|---|---|---|
| `GET` | `/logs/stream` | SSE stream of incoming Cowrie honeypot log events |
| `GET` | `/classification/stream` | SSE stream of MITRE ATT&CK classifications |
| `GET` | `/fixing/stream` | SSE stream of LangGraph remediation agent node events |
| `POST` | `/fixing/remediate` | Trigger a remediation workflow for a specific vulnerability |

---

## SSE Event Types

All streaming endpoints emit newline-delimited `data:` frames (standard SSE format).

| Event type | Emitted by | Description |
|---|---|---|
| `cowrie_log` | `/logs/stream` | Raw honeypot session event (IP, command, timestamp) |
| `mitre_classification` | `/classification/stream` | ATT&CK technique ID, name, severity, and confidence score |
| `node_start` | `/fixing/stream` | LangGraph agent node has started executing |
| `node_end` | `/fixing/stream` | LangGraph agent node has completed, includes output |
| `error` | Any stream | Pipeline error details |

For more detail on the SSE integration see [SSE_README.md](SSE_README.md).
