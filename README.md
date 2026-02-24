# Research Compass

**AI-powered research opportunity discovery platform** for students to find and explore research positions (labs, internships, PhD openings) that match their interests and profile. The project includes a FastAPI backend, a React frontend with authentication, semantic search over opportunities, and profile/resume management.

---

## Table of Contents

- [What This Repo Contains](#what-this-repo-contains)
- [What’s Already Built](#whats-already-built)
- [What’s Not Built / Next Steps](#whats-not-built--next-steps)
- [Architecture Overview](#architecture-overview)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Reference](#api-reference)
- [Environment & Configuration](#environment--configuration)
- [Development & Testing](#development--testing)

---

## What This Repo Contains

| Layer | Tech | Purpose |
|-------|------|--------|
| **Backend** | FastAPI, SQLAlchemy, PostgreSQL (pgvector), Alembic | REST API, auth, profiles, opportunities CRUD, embeddings, semantic search |
| **Frontend** | React 19, TypeScript, Vite, React Router, Tailwind | Sign up/in, dashboard, opportunity list/search, detail modal |
| **AI/ML** | OpenAI Embeddings (text-embedding-3-large) | Vector embeddings for users and opportunities; semantic search |
| **Auth** | JWT (access + refresh), bcrypt, refresh token storage in DB | Sign up, sign in, refresh, logout, protected routes |
| **Data** | SQLite (dev) or PostgreSQL + pgvector | Users, opportunities, matches, outreach, embeddings |

---

## What’s Already Built

### Backend (FastAPI)

- **App bootstrap**: FastAPI app with CORS, lifespan (DB init), health checks (`/`, `/health`).
- **Authentication** (`/api/auth`):
  - `POST /auth/signup` – register (email, password, name); returns JWT pair.
  - `POST /auth/signin` – login; returns JWT pair.
  - `POST /auth/refresh` – refresh access token using refresh token.
  - `POST /auth/logout` – revoke refresh token (requires auth).
  - `GET /auth/me` – current user (requires auth).
- **Users & profile** (`/api/profile`):
  - `POST /profile/upload-resume` – upload PDF resume; parse with `pdfplumber`; return structured data for review.
  - `POST /profile` – create/update full profile (university, major, experiences, skills, research interests, etc.).
  - `PATCH /profile` – partial profile update.
  - `GET /profile` – current user’s profile.
  - `GET /profile/{user_id}` – profile by user ID.
- **Opportunities** (`/api/opportunities`):
  - `GET /opportunities` – list with filters: `search`, `institution`, `funding_status`, `is_active`, pagination.
  - `GET /opportunities/{id}` – get one.
  - `POST /opportunities` – create (auth).
  - `PUT /opportunities/{id}` – update (auth).
  - `DELETE /opportunities/{id}` – soft delete (set `is_active=false`).
- **Semantic search** (same prefix `/api/opportunities`):
  - `POST /opportunities/search` – natural-language search: query → embedding → similarity search with optional filters (states, degree_level, is_remote, paid_type, hours). Returns ranked opportunities with similarity scores. **No auth required** for this endpoint.
  - `GET /opportunities/search/test` – check search setup (embeddings count, API key).
- **Embeddings** (`/api/embeddings`):
  - `POST /embeddings/users/{user_id}` – generate/store user embedding from research interests.
  - `POST /embeddings/opportunities/{opportunity_id}` – generate/store opportunity embedding.
  - `POST /embeddings/users/generate-all` – batch user embeddings.
  - `POST /embeddings/opportunities/generate-all` – batch opportunity embeddings.
  - `GET /embeddings/stats` – counts of users/opportunities with or without embeddings.
- **Database**:
  - Models: `User`, `Opportunity`, `Match`, `Outreach`, `RefreshToken`, `UserEmbedding`, `OpportunityEmbedding`.
  - Alembic migrations (auth, embeddings, vector dimensions, hard filters like location/degree/hours).
  - SQLite for dev; PostgreSQL + pgvector for vector search in production.
- **Utilities**:
  - Resume parser: PDF → text + structured fields (education, skills, experience, etc.) via `pdfplumber` and regex.
- **Config**: `pydantic-settings` (e.g. `DATABASE_URL`, `OPENAI_API_KEY`, `SECRET_KEY`, `CORS_ORIGINS`).
- **Tests**: Pytest with conftest, tests for models, CRUD, relationships.

### Frontend (React + Vite)

- **Routing**: `/signup`, `/signin`, `/dashboard`, `/` → dashboard; protected route wrapper.
- **Auth**: `AuthContext` (signUp, signIn, logout, refreshUser); token storage (localStorage); axios interceptors for Bearer token and refresh-on-401.
- **Pages**:
  - **SignUp** – email, password, name; validation; calls signup then redirects.
  - **SignIn** – email, password; validation; calls signin then redirects.
  - **Dashboard (Neo)** – list of opportunities from `GET /opportunities` with text search; cards with title, lab, PI, institution, topics, deadline, funding; detail modal; “Apply” / “View Source” links; logout.
- **Services**: `AuthService` + `TokenStorage`; `OpportunitiesService` (getOpportunities, getOpportunity, create, update, delete) using shared axios instance.
- **UI**: Neo-style design system (tokens, Card, Button, Badge, Input, Modal); Tailwind; loading/error/empty states.

### Data & Seeding

- **Seed script** (`backend/seed_opportunities.py`): Inserts sample opportunities (e.g. MIT Vision, Stanford NLP, Berkeley Robotics) so you can test list/detail and, after generating embeddings, semantic search.

---

## What’s Not Built / Next Steps

These are explicitly **not** implemented yet; good candidates for “what to develop further”:

1. **Matches API & UI**
   - Backend: No `/api/matches` or `/api/matches/{user_id}` to compute or return user–opportunity matches (scores, rationale). The `Match` model and DB exist; you need endpoints and logic (e.g. run semantic similarity, write to `matches` table).
   - Frontend: No “My Matches” or “Recommended for you” powered by match scores.

2. **Outreach API & UI**
   - Backend: No `/api/outreach/generate` (or similar) to generate outreach emails. The `Outreach` model exists; you need an endpoint (e.g. calling an LLM) and possibly “send”/“save” actions.
   - Frontend: No UI to generate or send outreach emails from an opportunity.

3. **Semantic search in the dashboard**
   - Backend: `POST /opportunities/search` is implemented and works without auth.
   - Frontend: Dashboard uses only `GET /opportunities` with text search. There is no UI that calls `POST /opportunities/search` (natural-language query + filters) or shows similarity scores. Adding a “Search by interests” input that calls this endpoint would complete the loop.

4. **Profile onboarding flow**
   - Backend: Profile create/update and resume upload/parse exist.
   - Frontend: No dedicated profile/edit or onboarding flow (e.g. after signup: upload resume, fill research interests, preferences). Dashboard doesn’t prompt or link to profile.

5. **Embedding triggers**
   - When a user updates research interests or an opportunity is created/updated, embeddings are not automatically regenerated. You could add background tasks or webhooks that call the embedding endpoints (or internal services) after profile/opportunity changes.

6. **Scraping / ingestion**
   - No scraper or ingestion pipeline (e.g. Bright Data or custom) to populate `opportunities` from external sites. Seed data is manual; production would need a way to add/update opportunities from the web.

7. **Production hardening**
   - Use of PostgreSQL + pgvector in production (migrations support it).
   - Env-based secrets (no default `SECRET_KEY` in production).
   - Optional: rate limiting, stricter CORS, logging, monitoring.

8. **Profile ↔ User model alignment**
   - Profile API uses `experience_level`; the `User` model in code uses `degree_level`. Migrations may have added `experience_level`; confirm the `User` model and migrations are in sync so profile updates persist correctly.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  Frontend (React + Vite)                                         │
│  - SignUp / SignIn / Dashboard (opportunity list + detail)       │
│  - AuthContext, ProtectedRoute, OpportunitiesService            │
└───────────────────────────────┬─────────────────────────────────┘
                                 │ HTTP (JWT in headers)
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  Backend (FastAPI)                                               │
│  - Auth, Profile, Opportunities CRUD, Search, Embeddings          │
│  - EmbeddingService (OpenAI), SearchService (vector similarity)  │
└───────────────────────────────┬─────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  Database (SQLite dev / PostgreSQL prod)                         │
│  - users, opportunities, matches, outreach, refresh_tokens       │
│  - user_embeddings, opportunity_embeddings (pgvector)            │
└─────────────────────────────────────────────────────────────────┘
```

- **Semantic search**: User/opportunity text → OpenAI embeddings → stored in `*_embeddings`. Search: query → embedding → cosine similarity (pgvector) + optional filters → ranked results.

---

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env` (see [Environment & Configuration](#environment--configuration)). For local dev you can skip `.env`; the app will use SQLite and default config.

```bash
python init_db.py
python seed_opportunities.py   # optional: sample data
python run.py
```

API: http://localhost:8000  
Docs: http://localhost:8000/docs  

### How to start the backend and see what’s working

1. **Start the server** (from repo root):
   ```bash
   cd backend
   source venv/bin/activate   # or: venv\Scripts\activate on Windows
   python init_db.py          # first time only (creates DB/tables)
   python seed_opportunities.py   # optional: add sample opportunities
   python run.py
   ```
   You should see something like: `Using SQLite: .../backend/data/research_compass.db`, `Database initialized`, and `Uvicorn running on http://0.0.0.0:8000`.

2. **Quick checks in the browser**:
   - **Health**: Open http://localhost:8000/health — should return `{"status":"healthy",...}`.
   - **API docs**: Open http://localhost:8000/docs — try endpoints from the Swagger UI.

3. **What works with SQLite (no `.env` required)**:
   - `GET /`, `GET /health`
   - `POST /api/auth/signup`, `POST /api/auth/signin`, `GET /api/auth/me`, `POST /api/auth/refresh`, `POST /api/auth/logout`
   - `GET /api/opportunities`, `GET /api/opportunities/{id}` (after seeding), `POST /api/opportunities` (with auth)
   - `GET /api/profile`, `POST /api/profile`, `PATCH /api/profile`, `POST /api/profile/upload-resume` (with auth)

4. **What needs extra setup**:
   - **Semantic search** (`POST /api/opportunities/search`): Needs **PostgreSQL + pgvector** and **`OPENAI_API_KEY`**. With SQLite, embeddings tables aren’t created by `init_db`; use PostgreSQL and run `alembic upgrade head` for full search.
   - **Embeddings** (`/api/embeddings/*`): Same as above — PostgreSQL + pgvector + `OPENAI_API_KEY`. On SQLite, embedding endpoints will fail if the embedding tables don’t exist.

5. **Suggested manual test flow** (with server running):
   - In Swagger UI (http://localhost:8000/docs): **POST /api/auth/signup** with `{"email":"you@example.com","password":"TestPass123","name":"Your Name"}` → copy `access_token`.
   - Click **Authorize**, paste `Bearer <access_token>` (or just the token if the UI has a Bearer field).
   - **GET /api/auth/me** → should return your user.
   - **GET /api/opportunities** → list (empty until you run `seed_opportunities.py`).
   - Run `python seed_opportunities.py` in another terminal, then **GET /api/opportunities** again to see sample data.

### Testing your routes

With the backend running (`python run.py`), you can test routes in three ways:

**1. Swagger UI (easiest)**  
Open **http://localhost:8000/docs**. You can:
- Try any endpoint (click “Try it out”, fill body, “Execute”).
- For protected routes: **Authorize** → enter `Bearer <your_access_token>` (get a token from `POST /api/auth/signup` or `POST /api/auth/signin` first).

**2. Script (backend folder)**  
From the `backend` directory (with the server running in another terminal):

```bash
pip install requests   # if needed
python test_routes.py
```

This hits: `/health`, `/`, signup (or signin), `/api/auth/me`, `/api/opportunities`, `/api/profile`, `/api/opportunities/search/test`.

**3. curl examples**

```bash
# Health
curl -s http://localhost:8000/health | jq

# Sign up (password must include upper, lower, and digit — e.g. TestPass123)
curl -s -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"TestPass123","name":"Your Name"}' | jq

# Sign in (save access_token from response)
curl -s -X POST http://localhost:8000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"TestPass123"}' | jq

# Protected route (replace TOKEN with access_token from signin/signup)
curl -s http://localhost:8000/api/auth/me -H "Authorization: Bearer TOKEN" | jq
curl -s http://localhost:8000/api/opportunities?limit=10 -H "Authorization: Bearer TOKEN" | jq
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173 (or the port Vite prints). Set `VITE_API_URL=http://localhost:8000` if the API is not on that host.

### Semantic search (after backend is running)

1. Set `OPENAI_API_KEY` in `backend/.env`.
2. Create opportunities (or run `seed_opportunities.py`).
3. Generate embeddings:  
   `POST /api/embeddings/opportunities/generate-all`  
   (and optionally for users)  
   `POST /api/embeddings/users/generate-all`
4. Call `POST /api/opportunities/search` with a JSON body, e.g.  
   `{"query": "machine learning for healthcare", "limit": 10}`.

---

## Project Structure

```
research-compass/
├── README.md                 # This file
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app, CORS, routes
│   │   ├── api/              # auth, profile, opportunities, embeddings, search
│   │   ├── core/             # config, auth (JWT, bcrypt)
│   │   ├── db/               # database, base
│   │   ├── models/           # User, Opportunity, Match, Outreach, RefreshToken, *Embedding
│   │   ├── schemas/           # auth, profile, search
│   │   ├── services/         # embeddings, search
│   │   └── utils/            # resume_parser
│   ├── alembic/              # migrations
│   ├── tests/
│   ├── init_db.py
│   ├── run.py
│   ├── seed_opportunities.py
│   ├── requirements.txt
│   ├── DATABASE.md
│   └── README.md
└── frontend/
    ├── src/
    │   ├── App.tsx
    │   ├── main.tsx
    │   ├── contexts/         # AuthContext
    │   ├── pages/            # SignUp, SignIn, DashboardNeo
    │   ├── components/       # ProtectedRoute, neo (Card, Button, Badge, Input, Modal)
    │   ├── services/         # auth, opportunities
    │   └── styles/           # tokens
    ├── package.json
    ├── vite.config.ts
    └── tailwind.config.js
```

---

## API Reference

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | No | API info |
| GET | `/health` | No | Health check |
| POST | `/api/auth/signup` | No | Register |
| POST | `/api/auth/signin` | No | Login |
| POST | `/api/auth/refresh` | No | Refresh tokens |
| POST | `/api/auth/logout` | Yes | Logout (revoke refresh token) |
| GET | `/api/auth/me` | Yes | Current user |
| POST | `/api/profile/upload-resume` | Yes | Upload & parse resume PDF |
| POST | `/api/profile` | Yes | Create/update full profile |
| PATCH | `/api/profile` | Yes | Partial profile update |
| GET | `/api/profile` | Yes | Current user profile |
| GET | `/api/profile/{user_id}` | Yes | Profile by user ID |
| GET | `/api/opportunities` | Yes | List opportunities (with filters) |
| GET | `/api/opportunities/{id}` | Yes | Get one opportunity |
| POST | `/api/opportunities` | Yes | Create opportunity |
| PUT | `/api/opportunities/{id}` | Yes | Update opportunity |
| DELETE | `/api/opportunities/{id}` | Yes | Soft delete opportunity |
| POST | `/api/opportunities/search` | No | Semantic search (query + optional filters) |
| GET | `/api/opportunities/search/test` | No | Search setup check |
| POST | `/api/embeddings/users/{user_id}` | No | Generate user embedding |
| POST | `/api/embeddings/opportunities/{id}` | No | Generate opportunity embedding |
| POST | `/api/embeddings/users/generate-all` | No | Batch user embeddings |
| POST | `/api/embeddings/opportunities/generate-all` | No | Batch opportunity embeddings |
| GET | `/api/embeddings/stats` | No | Embedding counts |

---

## Environment & Configuration

**Backend** (`backend/.env`):

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | DB connection | `sqlite:///./data/research_assistant.db` or `postgresql://user:pass@host:5432/db` |
| `OPENAI_API_KEY` | For embeddings & search | Required for semantic search |
| `SECRET_KEY` | JWT signing | Use a long random string in production |
| `CORS_ORIGINS` | Allowed origins | e.g. `["http://localhost:5173"]` |
| `ANTHROPIC_API_KEY` / `GOOGLE_API_KEY` | Optional future LLM use | - |

**Frontend**: `VITE_API_URL` (default `http://localhost:8000`) for API base URL.

---

## Development & Testing

- **Backend tests**: `cd backend && pip install -r requirements-test.txt && pytest` (see `backend/README.md` and `backend/DATABASE.md` for DB and testing notes).
- **Migrations**: `alembic revision --autogenerate -m "message"`, `alembic upgrade head`.
- **Frontend**: `npm run dev`, `npm run build`, `npm run lint`.

### Debugging “Sign up failed”

If the sign-up form always shows “Sign up failed”:

1. **Backend running?** The frontend shows a clearer message if the server is unreachable: “Cannot reach server. Is the backend running at http://localhost:8000?”
2. **Password rules** (backend requires): at least 8 characters, one uppercase, one lowercase, one digit. Use e.g. `TestPass123`.
3. **Validation errors** (422): The UI now shows the backend’s validation message (e.g. “password: Password must contain at least one uppercase letter”).
4. **Quick API check** (backend must be running):
   ```bash
   curl -s -X POST http://localhost:8000/api/auth/signup \
     -H "Content-Type: application/json" \
     -d '{"email":"test2@example.com","password":"TestPass123","name":"Test User"}' | jq
   ```
   If this succeeds, the backend is fine; if it fails, the response body explains why.

### Test user (avoid signing up every time)

Seed a fixed test user so you can sign in without registering repeatedly:

```bash
cd backend
source venv/bin/activate   # or venv\Scripts\activate on Windows
python seed_test_user.py
```

Then sign in in the app with:

- **Email:** `test@example.com`
- **Password:** `TestPass123`

Re-running `seed_test_user.py` resets this user’s password and name if you already created it.

### Testing the frontend without manual clicking

1. **Auth API only** (no browser): From the repo root, with the backend running:
   ```bash
   node frontend/scripts/test-auth.mjs
   ```
   This script calls `POST /api/auth/signin` (and optionally signup) and prints the response so you can confirm the backend and URL work.

2. **E2E in a real browser**: Install Playwright and run the E2E test (sign in + dashboard):
   ```bash
   cd frontend
   npx playwright install
   npm run test:e2e
   ```
   This opens a browser, signs in as the test user, and checks that the dashboard loads. Requires backend running and `python backend/seed_test_user.py` to have been run once.

---

## Summary

- **Already developed**: Full auth (signup/signin/refresh/logout), profile CRUD + resume upload/parse, opportunities CRUD, semantic search API, embeddings API, Match/Outreach DB models, React app with dashboard and opportunity list/detail. Ready for you to add matches UI, outreach API/UI, semantic search in the dashboard, profile onboarding, and scraping/ingestion.
- **Develop further**: Matches API & UI, outreach generation & UI, semantic search in frontend, profile onboarding, auto-embedding on profile/opportunity changes, opportunity scraping, and production hardening (PostgreSQL, secrets, optional rate limiting and monitoring).
