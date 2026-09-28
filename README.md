# 🐕 DOGFOOD Portal

> **An offline-first, open-source hackathon submission & judging platform, engineered for the DOGFOOD 2026 challenge.**

![Status](https://img.shields.io/badge/status-verified-brightgreen)
![Tier](https://img.shields.io/badge/tier-T1%20%2B%20T2-blue)
![Tests](https://img.shields.io/badge/acceptance-7%2F7%20PASS-brightgreen)
![License](https://img.shields.io/badge/license-MIT-yellow)
![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/framework-FastAPI-009688)
![Docker](https://img.shields.io/badge/docker-compose-2496ED)

---

## 📑 Table of Contents

1. [Overview](#-overview)
2. [Problem Statement](#-problem-statement)
3. [Solution](#-solution)
4. [Architecture](#-architecture)
5. [Sequence Diagrams](#-sequence-diagrams)
6. [Quick Start](#-quick-start)
7. [API Reference](#-api-reference)
8. [Security Model](#-security-model)
9. [Acceptance Verification](#-acceptance-verification)
10. [Repository Structure](#-repository-structure)
11. [Tech Stack](#-tech-stack)
12. [License](#-license)

---

## 🎯 Overview

**DOGFOOD Portal** is a self-contained hackathon management system that replaces fragmented tooling (spreadsheets, scattered forms, opaque judging) with a **single integrated portal**. It handles:

- 📝 Project submission & team formation
- 🎨 Public gallery browsing
- ⚖️ Weighted judge scoring & assignment
- 🔐 Backend-enforced role isolation
- 📊 CSV export for organizers
- ⏰ Server-side deadline enforcement

It runs **fully offline** via `docker compose up`, requires **no cloud accounts**, and passes **all 7 official acceptance checks**.

---

## 🚨 Problem Statement

```mermaid
mindmap
  root((Existing Hackathon Platforms))
    Weak Judging
      No weighted rubrics
      Spreadsheet math
      Manual normalization
    Poor Security
      Frontend-only hiding
      Peer scores leak via API
      No object-level authz
    Cloud Lock-in
      Hosted DB required
      External auth providers
      No offline mode
    Opaque Results
      No public API
      No verifiable audit trail
      Scraping needed
Organizers today are pushed toward brittle spreadsheets, manual scraping, and unverifiable result calculations. DOGFOOD Portal solves each of these directly.

✅ Solution
mermaid

graph LR
    A[Hackathon Organizer] -->|docker compose up| B[DOGFOOD Portal]
    B --> C[Public Gallery]
    B --> D[Judge Workflow]
    B --> E[CSV Export]
    B --> F[Deadline Enforcement]

    C -.->|Unauthenticated| G[Anonymous Visitors]
    D -.->|Session Cookie| H[Judges A/B]
    E -.->|Organizer Auth| I[Analytics/Prizes]
    F -.->|Backend Timestamp Check| J[Fixture Deadline]

    style B fill:#ff69b4,color:#fff
    style G fill:#90ee90
    style H fill:#87ceeb
    style I fill:#ffd700
    style J fill:#ff6b6b,color:#fff
🏗️ Architecture
High-Level Component Architecture
mermaid

graph TB
    subgraph Client[Client Layer]
        CLI[run.py Checker]
        WEB[Browser / curl]
    end

    subgraph Portal[DOGFOOD Portal - FastAPI]
        MW[CORS Middleware]
        RT[Route Handlers]
        AUTH[Session Cookie Validator]
        AUTHZ[Backend Authorization]
        SVC[Business Logic]
    end

    subgraph Data[Data Layer]
        FIX[fixtures.json]
        MEM[In-Memory Store]
    end

    subgraph Config[Configuration]
        TOML[.dogfood.toml]
    end

    CLI -->|HTTP| MW
    WEB -->|HTTP| MW
    TOML -.->|Routes + Auth Headers| CLI
    MW --> RT
    RT --> AUTH
    AUTH --> AUTHZ
    AUTHZ --> SVC
    SVC --> MEM
    FIX -->|Load on Boot| MEM

    style Portal fill:#e1f5ff
    style Data fill:#fff4e1
    style Config fill:#f0e1ff
Deployment Architecture (Offline-First)
mermaid

graph LR
    subgraph Host[Laptop / Local Machine]
        subgraph Docker[Docker Compose]
            APP[Portal Container<br/>python:3.11-slim<br/>uvicorn on :8080]
            VOL[Bind Mount: ./]
        end
        PORT[localhost:8080]
        NET[No Network Required]
    end

    APP -->|Reads| VOL
    APP -->|Exposes| PORT
    APP -.->|Zero Deps| NET

    style Docker fill:#2496ED,color:#fff
    style NET fill:#90ee90
🔁 Sequence Diagrams
T1: Public Gallery Access
mermaid

sequenceDiagram
    participant V as Anonymous Visitor
    participant P as Portal /projects
    participant F as fixtures.json

    V->>P: GET /projects (no auth)
    P->>F: Load projects
    F-->>P: 41 fixture projects
    P-->>V: 200 OK + JSON array
    Note over V,P: Public gallery — no authentication needed
T1: Deadline Enforcement (Closed Event)
mermaid

sequenceDiagram
    participant P as Participant
    participant S as Portal /projects/new
    participant D as Deadline Check
    participant F as fixtures.json

    P->>S: POST /projects/new<br/>Cookie: session=participant_session
    S->>D: Check submissions_close
    D->>F: Read event.submissions_close
    F-->>D: 2026-03-01T18:00:00Z
    D-->>S: Deadline PASSED
    S-->>P: 403 Forbidden
    Note over P,S: Server-side enforcement<br/>Frontend cannot override
T2: Judge Score Isolation (Critical Security Test)
mermaid

sequenceDiagram
    participant JB as Judge B
    participant P as Portal API
    participant AZ as Authorization Layer

    Note over JB: judge_b tries to read judge_a scores
    JB->>P: GET /api/judge/scores?judge=judge_a<br/>Cookie: session=judge_b_session
    P->>AZ: Validate session + target
    AZ->>AZ: session=judge_b<br/>target=judge_a<br/>MISMATCH!
    AZ-->>P: DENY
    P-->>JB: 403 Forbidden
    Note over JB,P: 🔒 Backend-enforced isolation<br/>Hiding buttons is NOT security
T2: CSV Export (Organizer Only)
mermaid

sequenceDiagram
    participant O as Organizer
    participant P as Portal /api/export.csv
    participant CSV as CSV Generator
    participant F as fixtures.json

    O->>P: GET /api/export.csv<br/>Cookie: session=organizer_session
    P->>P: Validate role=organizer
    P->>F: Load projects
    F-->>P: Project data
    P->>CSV: Generate RFC-4180 CSV
    CSV-->>P: CSV rows
    P-->>O: 200 OK + text/csv
    Note over O,P: Formula-injection protected
🚀 Quick Start
Option A: Docker (Recommended for Judges)
Shell

# Start the portal
docker compose up --build

# In another terminal, run the acceptance checker
python run.py .dogfood.toml

# Teardown
docker compose down
Option B: Local Python
Shell

# Install dependencies
pip install -r requirements.txt

# Start server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080

# Run acceptance checker (in another terminal)
python run.py .dogfood.toml
The portal will be available at http://localhost:8080.

📡 API Reference
MethodEndpointAuth RequiredDescription
GET/NoneAPI root info
GET/healthNoneLiveness probe
GET/readyNoneReadiness probe
GET/projectsNonePublic gallery (fixture projects)
POST/projects/newParticipantSubmit project (blocked when deadline passed)
GET/api/judge/scoresJudgeRetrieve own scores
GET/api/judge/scores?judge=XJudge (self only)Returns 403 if X ≠ self
GET/api/export.csvOrganizerExport all data as CSV
🔐 Security Model
mermaid

graph TD
    REQ[Incoming HTTP Request] --> COOKIE{Session Cookie?}
    COOKIE -->|Missing| U401[401 Unauthorized]
    COOKIE -->|Present| ROLE{Extract Role}

    ROLE -->|participant| PART{Endpoint = judge/*?}
    ROLE -->|judge_a / judge_b| JUDGE{Query targets peer?}
    ROLE -->|organizer| ORG[✅ Allow All]

    PART -->|Yes| F403A[403 Forbidden]
    PART -->|No| ALLOW1[✅ Allow]

    JUDGE -->|Yes| F403B[403 Forbidden]
    JUDGE -->|No| ALLOW2[✅ Return Own Scores]

    style U401 fill:#ff6b6b,color:#fff
    style F403A fill:#ff6b6b,color:#fff
    style F403B fill:#ff6b6b,color:#fff
    style ORG fill:#90ee90
    style ALLOW1 fill:#90ee90
    style ALLOW2 fill:#90ee90
✅ Acceptance Verification
The portal is verified by the official DOGFOOD 2026 acceptance suite (run.py).

text

DOGFOOD 2026 acceptance report
portal: http://localhost:8080
claimed: T1 T2
fixtures: fixtures.json

T1  gallery is public ................. PASS
T1  project from fixtures shown ....... PASS
T1  closed event refuses submissions .. PASS
T2  judge sees own scores ............. PASS
T2  judge cannot see peer scores ...... PASS
T2  participant blocked ............... PASS
T2  csv export works .................. PASS

claimed T1 T2, verified T1 T2
📁 Repository Structure
text

dogfood/
├── app/
│   ├── main.py                  # Core FastAPI engine (all 7 routes)
│   ├── api/                     # Router modules
│   ├── core/                    # Auth, config, security
│   ├── models/                  # SQLAlchemy models
│   ├── schemas/                 # Pydantic schemas
│   └── services/                # Seed, normalization, CSV export
├── docs/                        # Architecture & PRD docs
├── fixtures.json                # Seed data (41 projects, 30 judges)
├── .dogfood.toml                # Checker configuration
├── run.py                       # Official acceptance checker
├── acceptance-report.txt        # 7/7 PASS receipt
├── Dockerfile                   # Container definition
├── docker-compose.yml           # Offline orchestration
├── requirements.txt             # Python dependencies
├── LICENSE                      # MIT License
└── README.md                    # This file
🛠️ Tech Stack
LayerChoiceReason
LanguagePython 3.11Zero-install stdlib for checker
FrameworkFastAPIAsync, OpenAPI native, type-safe
ServerUvicornProduction-grade ASGI
Persistencefixtures.json + SQLAlchemyDeterministic offline seed
AuthSession cookiesSimple, aligns with checker contract
ContainerDocker ComposeSingle-command offline startup
LicenseMITOSI-approved, permissive
📜 License
This project is licensed under the MIT License — see the LICENSE file for details.
