# HackEurope – AI-Powered Honeypot Threat Monitor

An AI-powered cybersecurity platform that captures attacker activity via a Cowrie SSH honeypot, classifies threats using MITRE ATT&CK with Google Gemini, and streams real-time alerts and remediation guidance to a React dashboard.

---

## Architecture

```
Cowrie Honeypot  ──►  Wazuh Manager  ──►  FastAPI Backend  ──►  React Frontend
   (SSH trap)         (rule matching)      (SSE streams)         (live dashboard)
                                                │
                                         Google Gemini LLM
                                      (MITRE ATT&CK classifier)
```

1. **Cowrie** acts as a fake SSH server, capturing every login attempt and command.
2. **Wazuh** matches raw events against XML detection rules.
3. The **FastAPI backend** exposes Server-Sent Event (SSE) endpoints that stream live logs, risk scores, attack chains, and MITRE ATT&CK classifications to the frontend.
4. **Google Gemini** (via `metra_classifier`) analyses honeypot logs and maps attacker behaviour to MITRE ATT&CK tactics and techniques.
5. The **React frontend** visualises all of the above in real-time and lets operators generate and deploy new Wazuh rules with a single click using natural language.

---

## Project Structure

```
HackEurope/
├── backend/                  # FastAPI application
│   ├── api/
│   │   ├── classification.py # SSE – MITRE ATT&CK classifications
│   │   ├── dashboard.py      # SSE – live logs, risk scores, attack chains
│   │   ├── fixer.py          # SSE – automated remediation status
│   │   ├── logs.py           # SSE – raw Cowrie log stream
│   │   ├── rules.py          # REST – generate & deploy Wazuh rules via LLM
│   │   └── router.py
│   ├── wazuh_rules/          # Wazuh rule matching logic
│   └── main.py
├── frontend/                 # React + Vite dashboard
│   └── src/
│       ├── components/       # Sidebar, Layout, ClassificationDashboard, …
│       └── pages/            # Dashboard, Analytics, Settings, …
├── metra_classifier/         # Standalone MITRE ATT&CK classifier
│   ├── main.py               # Classification workflow entry point
│   ├── prompts.py            # Gemini system prompt & output schema
│   └── env_setup.py
├── llm/                      # Shared LLM helper (Gemini API call)
├── wazuh-rules/              # Deployed Wazuh XML rule files (Docker volume)
├── data/                     # Sample honeypot logs & MITRE ATT&CK dataset
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python      | 3.11+   |
| Node.js     | 18+     |
| Docker & Docker Compose | any recent |
| Google Gemini API key | — |

---

## Quick Start

### 1 – Clone & configure

```bash
git clone https://github.com/PawelPopkiewicz/HackEurope.git
cd HackEurope
```

Create a `.env` file in the project root:

```
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 2 – Docker Compose (recommended)

Starts Wazuh Manager, Cowrie honeypot, and the FastAPI backend together:

```bash
docker-compose up --build
```

| Service | Port |
|---------|------|
| FastAPI backend | `http://localhost:8000` |
| Wazuh API       | `http://localhost:55000` |
| Cowrie SSH trap | `localhost:2222`         |

### 3 – Local development (without Docker)

**Backend**

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

**Frontend**

```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

The frontend dev server starts at `http://localhost:5173`.

---

## API Endpoints

All endpoints are served under `/api/v1`.

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/logs/stream`                  | Raw Cowrie JSON events (SSE) |
| `GET`  | `/classification/stream`        | MITRE ATT&CK classifications (SSE) |
| `GET`  | `/fixing/stream`                | Remediation agent status (SSE) |
| `POST` | `/fixing/remediate`             | Trigger a remediation workflow |
| `GET`  | `/dashboard/live-logs`          | All Cowrie events, live (SSE) |
| `GET`  | `/dashboard/rejected-logs`      | Events matched by a Wazuh rule (SSE) |
| `GET`  | `/dashboard/risk-scores`        | Events annotated with risk score (SSE) |
| `GET`  | `/dashboard/attack-chains`      | Correlated multi-step attack chains (SSE) |
| `POST` | `/rules/generate`               | Generate a Wazuh XML rule via LLM |
| `POST` | `/rules/deploy`                 | Save a generated rule to disk |

---

## MITRE ATT&CK Classifier

The standalone classifier in `metra_classifier/` reads honeypot logs and a MITRE ATT&CK dataset, then calls Google Gemini to produce a structured JSON report:

```bash
cd metra_classifier
python main.py
```

Output schema:

```json
{
  "event_type": "attack_session",
  "analysis": { "summary": "...", "confidence": "high", "severity": "critical" },
  "mitre_attack": [
    { "tactic_id": "TA0001", "tactic_name": "Initial Access",
      "technique_id": "T1110", "technique_name": "Brute Force",
      "evidence": ["12 failed logins from 185.220.101.47"] }
  ],
  "mitigations": [
    { "mitigation_id": "M1036", "mitigation_name": "Account Use Policies",
      "description": "Enforce account lockout after N failed attempts." }
  ]
}
```

---

## Risk Scoring

Events are scored 0–100 and labelled automatically:

| Score  | Severity | Colour |
|--------|----------|--------|
| 0–29   | Low      | green  |
| 30–59  | Medium   | amber  |
| 60–79  | High     | orange |
| 80–100 | Critical | red    |

---

## Wazuh Rule Generation

Operators can describe a detection rule in plain English on the **Rules Config** page. The backend calls Gemini to produce valid Wazuh XML, which can be deployed directly to the `wazuh-rules/` volume shared with the Wazuh Manager container.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | ✅ | Google Gemini API key |

---

## Tech Stack

- **Backend**: Python 3.11, FastAPI, LangGraph, LangChain, Uvicorn
- **Frontend**: React 18, Vite, Tailwind CSS, React Flow
- **AI**: Google Gemini (`gemini-2.5-flash`)
- **Security**: Cowrie (SSH honeypot), Wazuh (SIEM/rule engine)
- **Infrastructure**: Docker, Docker Compose
