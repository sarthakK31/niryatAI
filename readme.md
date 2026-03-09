# Niryat AI

AI-guided export readiness platform for Indian MSMEs. Niryat helps first-time exporters navigate the complex journey from registration to first shipment through an intelligent agent, structured readiness tracking, and trade market intelligence.

Built for the "AI for Bharat" hackathon.

---

## What It Does

**Export Readiness Tracker** — A 10-step structured journey covering IEC registration, HS code compliance, buyer discovery, documentation, logistics, and payment setup. Users check off substeps and see their overall readiness percentage.

**AI Chat Agent** — A constrained Strands agent backed by AWS Bedrock Claude. It queries live trade data, retrieves export guidance documents from S3, tracks user progress, and analyzes uploaded documents via vision models. It will not hallucinate: all market data comes from tool calls.

**Market Intelligence** — Trade statistics for 100+ country-product pairs, including 5-year import growth, opportunity scores, volatility, and AI-generated summaries. Visualized on an interactive world map, filtered to the user's registered HS codes.

**HS Code Configuration** — Users register product codes with autocomplete search. All market queries, dashboard data, and agent context are scoped to these codes.

---

## Architecture

```
CloudFront (HTTPS)
       |
  _____|_____
 |           |
S3          EC2 (Docker)
Frontend    FastAPI:8000
            |
     _______|_______
    |        |      |
   RDS    Bedrock   S3
Postgres  Claude   Docs
```

A single CloudFront URL routes `/api/*` to the EC2 backend and everything else to the S3-hosted Next.js static build. No separate subdomains, no mixed-content issues.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js, TypeScript, Tailwind CSS v4 |
| Backend | FastAPI, Python, Uvicorn |
| AI Agent | Strands Agents framework |
| LLM | AWS Bedrock Claude 3.5 Sonnet (Gemini / Ollama as fallback) |
| Vision | Bedrock Claude vision, Gemini inline, Ollama qwen2.5vl |
| Database | PostgreSQL 15 (AWS RDS) |
| Storage | AWS S3 (frontend static, export docs) |
| Infra | AWS EC2, CloudFront, VPC, IAM |
| IaC | AWS CloudFormation |
| Auth | JWT (HS256), bcrypt |

---

## Key Design Decisions

**No hallucination by design** — The agent's system prompt enforces six rules: always use tools, only SELECT queries, cite sources, simplify language for non-technical users. Market data is never generated; it is always queried.

**No external memory service** — Chat history is stored in PostgreSQL. No Mem0, no in-memory dict, no vendor lock-in. The agent receives the last 10 messages as context on each request.

**Multi-provider LLM** — Switching between Bedrock, Gemini, and Ollama is a single env var change. Vision processing has three parallel implementations under the same interface.

**Read-only agent database access** — The `query_market_data` tool validates queries with regex before execution. INSERT, UPDATE, DELETE, and DROP are blocked. Only three whitelisted tables are accessible.

**Dual-origin CloudFront** — One HTTPS URL for judges. SPA routing handled by returning `index.html` on 404/403 from the S3 origin.

---

## Local Development

**Prerequisites**: Docker, Node.js 18+, Python 3.11+, PostgreSQL client

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

Set environment variables in `backend/.env`:
```
DATABASE_URL=postgresql://...
JWT_SECRET=...
MODEL_PROVIDER=ollama        # or bedrock, gemini
BEDROCK_REGION=us-east-1
S3_BUCKET=niryat-export-docs
```

---

## Deployment

One-command deploy to AWS:

```bash
./deploy/deploy.sh \
  --key-pair YOUR_KEY_PAIR \
  --db-password "StrongPassword123" \
  --key-file /path/to/key.pem
```

This provisions the full CloudFormation stack (VPC, EC2, RDS, S3, CloudFront, IAM), deploys the backend via Docker, builds and uploads the frontend to S3, and prints the CloudFront URL. Total time: ~25 minutes.

Estimated cost for a 1-hour demo: $2-5. RDS is free tier eligible for 12 months.

---

## Project Structure

```
niryatAI/
  backend/
    app/
      main.py              # FastAPI app, route registration
      services/
        agent.py           # Strands agent, tool definitions, multi-model support
        market_intel.py    # Trade data queries, opportunity scoring
        chat_persistence.py # Session and message storage
        hs_lookup.py       # HS code search and description lookup
      routes/              # auth, chat, dashboard, markets, profile, readiness
      database.py          # ThreadedConnectionPool, context manager
      middleware.py        # JWT verification dependency
  frontend/
    src/
      app/                 # Next.js app router pages
      components/          # ExportMap, AuthLayout, Sidebar, ThemeProvider
      lib/api.ts           # API client with namespaced methods
  db-init/
    01-schema.sql          # Full schema with seed data for export steps
  deploy/
    cloudformation.yaml    # Full AWS infrastructure definition
    deploy.sh              # One-command deployment script
    DEPLOY.md              # Deployment documentation
```

---

## API Overview

All routes require `Authorization: Bearer <token>` except `/auth/*`.

| Route | Purpose |
|---|---|
| `POST /auth/register` | Create account |
| `POST /auth/login` | Login, receive JWT |
| `GET /dashboard/` | Readiness %, top markets, map data |
| `POST /chat/send` | Send message with optional image |
| `GET /chat/sessions` | List conversations |
| `GET /readiness/steps` | Full 10-step export journey |
| `POST /readiness/mark` | Mark substep complete |
| `GET /markets/top` | Ranked markets by HS code |
| `GET /markets/map-data` | Country coordinates + scores |
| `GET /hs-codes/search` | Autocomplete HS code search |

---

## Team

Built at AI for Bharat hackathon.
