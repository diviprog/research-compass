# Research Compass

Finding research opportunities is broken. Lab openings are scattered across hundreds of professor websites, listings go stale, and cold emailing a PI without context is a shot in the dark. Research Compass fixes this: describe your research interests in plain English, get semantically ranked lab openings, and generate a personalized cold email to the PI — all in one place.

**Winner of CalHacks 12.0.**

---

## How it works

1. **Sign up and build your profile** — enter your university, major, graduation year, and research interests. Upload your resume to auto-populate your background.
2. **Search in natural language** — type something like "machine learning for medical imaging" or "reinforcement learning in robotics". Research Compass embeds your query and ranks all opportunities by semantic similarity.
3. **Review ranked matches** — each result shows a similarity score (e.g. "92% match"), PI name, lab, institution, research topics, deadline, and funding status.
4. **Generate personalized outreach** — click "Generate Email" on any opportunity to get a tailored cold email to the PI based on your profile and the lab's work.

---

## Tech stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend | FastAPI + SQLAlchemy | Async Python, automatic OpenAPI docs, clean dependency injection |
| Database | PostgreSQL + pgvector | Keeps vectors co-located with relational data in one Postgres instance — no separate vector DB to operate |
| Embeddings | OpenAI text-embedding-3-large | MTEB retrieval score ~64.6; uses Matryoshka Representation Learning so dimensions can be reduced from 3072 to 256 with minimal quality loss |
| Frontend | React 19 + TypeScript + Vite | Type-safe, fast HMR, modern React features |
| Styling | Tailwind + custom design system | Rapid, consistent UI without a heavy component library |
| Auth | JWT (access + refresh) + bcrypt | Stateless, scalable; refresh tokens stored in DB for revocation |
| Email generation | GPT-4o | High-quality, context-aware cold email drafts personalized to student profile |
| Resume parsing | pdfplumber + regex | Lightweight, open-source; no vendor lock-in |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  Frontend (React + Vite)                                          │
│  Profile · Dashboard (semantic search + results) · Outreach email │
└────────────────────────────────┬─────────────────────────────────┘
                                  │ HTTPS (JWT bearer)
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│  Backend (FastAPI)                                                │
│  Auth · Profile · Opportunities CRUD · Semantic Search            │
│  Embeddings · Outreach generation (GPT-4o)                        │
└───────────────┬──────────────────────────────┬────────────────────┘
                │                              │
                ▼                              ▼
┌──────────────────────────────┐  ┌──────────────────────────────┐
│  PostgreSQL + pgvector       │  │  OpenAI API                  │
│  Users, opportunities,       │  │  text-embedding-3-large      │
│  embeddings, outreach        │  │  GPT-4o (email generation)   │
└──────────────────────────────┘  └──────────────────────────────┘
```

### Semantic search pipeline

1. **Query** — user submits a natural-language search string.
2. **Embed** — the query is sent to OpenAI `text-embedding-3-large`, producing a 3072-dimensional vector.
3. **Similarity search** — pgvector computes cosine distance between the query vector and all pre-computed opportunity embeddings stored in PostgreSQL.
4. **Hard filters** — results are optionally narrowed by location, degree level, remote status, paid type, and weekly hours.
5. **Ranked results** — opportunities return sorted by similarity score (0–1), displayed as a percentage match on each card.

`text-embedding-3-large` uses Matryoshka Representation Learning, so dimensions can be truncated to 256 with minimal retrieval quality loss — useful if storage cost matters. For higher retrieval performance, Voyage AI `voyage-3-large` and Google `Gemini Embedding 2` outperform it on MTEB retrieval benchmarks if re-embedding the corpus is acceptable.

---

## Features

- **Semantic search** — natural-language queries over all opportunities, ranked by cosine similarity via pgvector
- **JWT authentication** — sign up / sign in / refresh / logout with bcrypt-hashed passwords and refresh token revocation
- **Profile + resume parsing** — upload a PDF resume; pdfplumber extracts education, skills, and research summary to auto-populate your profile
- **Opportunity CRUD** — create, list, filter, update, and soft-delete research opportunities
- **Outreach email generation** — GPT-4o generates a personalized cold email to the PI using your profile and the opportunity details; saved as a draft

---

## Quick start

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python init_db.py
python seed_opportunities.py   # optional: load sample data
python run.py
```

API: http://localhost:8000 · Docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

> Set `OPENAI_API_KEY` in `backend/.env` to enable semantic search and outreach generation. For production-grade vector search, use PostgreSQL + pgvector and run `alembic upgrade head`.

---

## Environment variables

**`backend/.env`**

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | `sqlite:///./data/research_compass.db` (dev) or `postgresql://user:pass@host/db` |
| `OPENAI_API_KEY` | Required for semantic search and outreach generation |
| `SECRET_KEY` | JWT signing secret — use a long random string in production |
| `CORS_ORIGINS` | Allowed frontend origins, e.g. `["http://localhost:5173"]` |

**Frontend**: set `VITE_API_URL` (default `http://localhost:8000`).

---

## Project structure

```
research-compass/
├── backend/
│   ├── app/
│   │   ├── api/          # auth, profile, opportunities, search, embeddings, outreach
│   │   ├── core/         # JWT, bcrypt, config
│   │   ├── db/           # SQLAlchemy session
│   │   ├── models/       # User, Opportunity, Match, Outreach, *Embedding
│   │   ├── schemas/      # Pydantic request/response models
│   │   ├── services/     # EmbeddingService, SearchService
│   │   └── utils/        # resume_parser
│   ├── alembic/          # migrations
│   ├── init_db.py
│   ├── seed_opportunities.py
│   └── run.py
└── frontend/
    └── src/
        ├── contexts/     # AuthContext
        ├── pages/        # SignUp, SignIn, DashboardNeo, Profile, OutreachEmail
        ├── components/   # neo design system (Card, Button, Badge, Input, Modal)
        └── services/     # auth, opportunities, profile
```
