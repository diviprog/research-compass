# Backend routes – working status

Summary of all API routes and what’s **working** vs what you still need to **fill in or depend on**.

**Base URL:** `http://localhost:8000`  
**API prefix:** `/api`

---

## ✓ Working (verified with SQLite + `test_routes.py`)

These respond correctly with the current backend and SQLite.

| Method | Path | Auth | Notes |
|--------|------|------|--------|
| GET | `/` | No | API info |
| GET | `/health` | No | Health check |
| POST | `/api/auth/signup` | No | 201 created; 400 if email exists |
| POST | `/api/auth/signin` | No | 200 + tokens |
| POST | `/api/auth/refresh` | No | Body: `refresh_token` |
| POST | `/api/auth/logout` | Yes | Body: `refresh_token` |
| GET | `/api/auth/me` | Yes | Current user |
| GET | `/api/profile` | Yes | Current user’s profile |
| GET | `/api/profile/{user_id}` | Yes | Any user’s profile by ID |
| POST | `/api/profile` | Yes | Create/update full profile (required: university, major, graduation_year, research_interests) |
| PATCH | `/api/profile` | Yes | Partial profile update |
| GET | `/api/opportunities` | Yes | List; query: skip, limit, is_active, search, institution, funding_status |
| GET | `/api/opportunities/{id}` | Yes | Single opportunity |
| POST | `/api/opportunities` | Yes | Create (admin/scraper) |
| PUT | `/api/opportunities/{id}` | Yes | Update |
| DELETE | `/api/opportunities/{id}` | Yes | Soft delete (sets is_active=false) |
| GET | `/api/opportunities/search/test` | No | Search readiness (embeddings count, etc.) |
| GET | `/api/embeddings/stats` | No | Counts: users/opportunities with and without embeddings |

---

## ⚠ Working but need extra setup

Implemented and correct, but they depend on **PostgreSQL + pgvector** and/or **OPENAI_API_KEY**. With SQLite only they fail or aren’t used.

| Method | Path | Auth | Requirement | Gap to fill |
|--------|------|------|-------------|-------------|
| POST | `/api/opportunities/search` | No | PostgreSQL + pgvector, OPENAI_API_KEY, opportunity embeddings | Run `alembic upgrade head` on Postgres; generate embeddings; then search works. |
| POST | `/api/embeddings/users/{user_id}` | No | PostgreSQL + pgvector, OPENAI_API_KEY | Same as above. |
| POST | `/api/embeddings/opportunities/{id}` | No | PostgreSQL + pgvector, OPENAI_API_KEY | Same as above. |
| POST | `/api/embeddings/users/generate-all` | No | PostgreSQL + pgvector, OPENAI_API_KEY | Batch user embeddings. |
| POST | `/api/embeddings/opportunities/generate-all` | No | PostgreSQL + pgvector, OPENAI_API_KEY | Batch opportunity embeddings. |

---

## ✓ Implemented but not in test script

These are in the codebase and work; they’re just not called by `test_routes.py`.

| Method | Path | Auth | Notes |
|--------|------|------|--------|
| POST | `/api/profile/upload-resume` | Yes | Multipart PDF upload; parses resume and returns structured data. Test via Swagger or frontend. |

---

## ✗ Not implemented (gaps to build)

No backend route exists yet. Models/DB may exist.

| Intended route | Purpose | What to build |
|----------------|---------|----------------|
| `GET /api/matches` or `GET /api/matches/{user_id}` | User’s opportunity matches (scores, rationale) | Endpoint(s) that compute/read from `matches` table and return list for a user. |
| `POST /api/outreach/generate` (or similar) | Generate outreach email for an opportunity | Endpoint that takes user + opportunity (or IDs), calls an LLM, returns (and optionally stores in `outreach` table). |

---

## Quick reference: all routes in one list

- `GET /` — working  
- `GET /health` — working  
- `POST /api/auth/signup` — working  
- `POST /api/auth/signin` — working  
- `POST /api/auth/refresh` — working  
- `POST /api/auth/logout` — working  
- `GET /api/auth/me` — working  
- `GET /api/profile` — working  
- `GET /api/profile/{user_id}` — working  
- `POST /api/profile` — working  
- `PATCH /api/profile` — working  
- `POST /api/profile/upload-resume` — working (not in test script)  
- `GET /api/opportunities` — working  
- `GET /api/opportunities/{id}` — working  
- `POST /api/opportunities` — working  
- `PUT /api/opportunities/{id}` — working  
- `DELETE /api/opportunities/{id}` — working  
- `POST /api/opportunities/search` — needs Postgres + pgvector + OpenAI  
- `GET /api/opportunities/search/test` — working  
- `POST /api/embeddings/users/{user_id}` — needs Postgres + pgvector + OpenAI  
- `POST /api/embeddings/opportunities/{id}` — needs Postgres + pgvector + OpenAI  
- `POST /api/embeddings/users/generate-all` — needs Postgres + pgvector + OpenAI  
- `POST /api/embeddings/opportunities/generate-all` — needs Postgres + pgvector + OpenAI  
- `GET /api/embeddings/stats` — working  
- **Matches** — not implemented (gap)  
- **Outreach (e.g. generate email)** — not implemented (gap)

Use this to see what’s done and what to implement or wire up next.
