# Implementation Status

Developer handoff document. Describes what exists, what works, what is partial or broken, and known TODOs.

---

## Project structure

Every file (excluding `node_modules`, `venv`, `__pycache__`, `.git`) with a one-line description.

```
./
├── .gitignore                          # Git ignore patterns
├── README.md                           # Project overview, quick start, API table, env vars
├── IMPLEMENTATION_STATUS.md            # This file

backend/
├── .env                                # Local env (API keys, DATABASE_URL); gitignored
├── BACKEND_ROUTES.md                   # Backend route list and status notes
├── DATABASE.md                         # Database and migration documentation
├── README.md                           # Backend setup and run instructions
├── alembic.ini                         # Alembic config for migrations
├── alembic/
│   ├── __init__.py                     # Package init
│   ├── env.py                          # Alembic env (DB URL, target_metadata)
│   ├── script.py.mako                  # Migration script template
│   └── versions/
│       ├── __init__.py
│       ├── 553a7346f34d_update_vector_dimensions_to_3072.py  # Vector dim 3072 for embeddings
│       ├── 5bd4932ea643_add_authentication_support.py      # Auth, refresh_tokens
│       └── 913acfd7890d_add_embeddings_and_hard_filters.py # Embedding tables, filters
├── app/
│   ├── __init__.py
│   ├── agents/__init__.py              # Empty; placeholder for future agents
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py                     # Signup, signin, refresh, logout, GET /me
│   │   ├── embeddings.py               # Generate/store user & opportunity embeddings, stats
│   │   ├── opportunities.py            # CRUD for opportunities + list with filters
│   │   ├── outreach.py                 # POST /generate — cold email via GPT-4o, save Outreach
│   │   ├── profile.py                   # Upload resume, GET/POST/PATCH profile, GET by user_id
│   │   ├── scrape.py                   # POST /run — trigger UCLA scraper (no auth)
│   │   └── search.py                   # POST /search semantic search, GET /search/test
│   ├── core/
│   │   ├── __init__.py
│   │   ├── auth.py                     # JWT create/decode, get_current_user, hash_password, authenticate_user
│   │   └── config.py                   # Pydantic settings (SECRET_KEY, CORS, DB, API keys)
│   ├── db/
│   │   ├── __init__.py                 # Re-exports get_db, init_db, engine, etc.
│   │   ├── base.py                     # SQLAlchemy declarative Base
│   │   └── database.py                 # Engine, SessionLocal, get_db, init_db (SQLite-safe), reset_db
│   ├── models/
│   │   ├── __init__.py
│   │   ├── match.py                    # Match model (user_id, opportunity_id, score, rationale)
│   │   ├── opportunity.py              # Opportunity model (title, description, lab, PI, topics, etc.)
│   │   ├── opportunity_embedding.py    # opportunity_id, embedding vector, model_name, text_for_embedding
│   │   ├── outreach.py                 # Outreach model (user_id, opportunity_id, generated_email)
│   │   ├── refresh_token.py            # RefreshToken (token, user_id, expires_at, is_revoked)
│   │   ├── user.py                     # User model (auth, profile, research_interests, degree_level, etc.)
│   │   └── user_embedding.py           # UserEmbedding (user_id, embedding vector, model_name)
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py                     # UserSignUp, UserSignIn, TokenRefresh, AuthResponse, UserResponse
│   │   ├── profile.py                  # Experience, Publication, ProfileCreate, ProfileUpdate, ProfileResponse
│   │   └── search.py                   # SearchRequest, SearchFilters, SearchResultItem, SearchResponse
│   ├── services/
│   │   ├── __init__.py
│   │   ├── embeddings.py               # EmbeddingService — OpenAI embeddings, store in user/opportunity_embedding
│   │   ├── search.py                   # SearchService — pgvector cosine similarity + filters
│   │   └── (search uses embeddings; search API has SQLite numpy fallback in search.py)
│   ├── utils/
│   │   ├── __init__.py
│   │   └── resume_parser.py            # PDF → text, skills, education (university, major, graduation_year), GPT-4o research_summary, raw_text
│   └── main.py                         # FastAPI app, CORS, lifespan (init_db), mounts all API routers
├── data/
│   └── research_compass.db             # SQLite database file (created by init_db)
├── init_db.py                          # Script to run init_db() and create tables
├── pytest.ini                          # Pytest config
├── requirements.txt                    # Python dependencies (FastAPI, SQLAlchemy, OpenAI, bcrypt, etc.)
├── run.py                              # Starts uvicorn (app.main:app, port 8000, reload)
├── scrape_ucla.py                      # Standalone scraper: research-labs → professors → DuckDuckGo → GPT-4o → DB; title uses "Professor" if last name unknown
├── seed_opportunities.py               # Seeds 15 sample opportunities into DB (clears existing)
├── seed_test_user.py                   # Seeds test@example.com / TestPass123 for dev (create or update)
├── test_embeddings.py                  # Ad-hoc test for embedding generation
├── test_routes.py                      # Script to hit health, auth, opportunities, profile, search/test
├── test_search.py                      # Ad-hoc test for search
├── tests/
│   ├── __init__.py
│   ├── conftest.py                     # Pytest fixtures (db session, test client)
│   ├── test_crud_operations.py          # CRUD tests for opportunities
│   ├── test_models.py                  # Model tests
│   └── test_relationships.py          # Relationship tests
└── uploads/
    └── resumes/                        # Uploaded resume PDFs (profile upload-resume)
        └── *.pdf

frontend/
├── .gitignore
├── README.md
├── components.json                     # Component config (e.g. shadcn-style)
├── e2e/
│   └── auth-dashboard.spec.ts         # Playwright E2E: sign in with test user, assert dashboard
├── index.html                          # HTML entry
├── package-lock.json
├── package.json                        # Scripts (dev, build, lint, preview, test:e2e), deps
├── playwright.config.ts                # Playwright baseURL, webServer for dev, chromium
├── postcss.config.js
├── public/
│   └── vite.svg
├── scripts/
│   └── test-auth.mjs                  # Node script: GET health, POST signin, GET /me (no browser)
├── src/
│   ├── App.css
│   ├── App.tsx                         # Router, AuthProvider, routes: signup, signin, dashboard, profile, outreach, redirects
│   ├── assets/
│   │   └── react.svg
│   ├── components/
│   │   ├── ProtectedRoute.tsx         # Wraps protected pages; redirects to /signin if not authenticated
│   │   └── neo/
│   │       ├── Badge.tsx               # Badge variants (primary, secondary, danger, etc.)
│   │       ├── Button.tsx              # Button with variants, sizes, optional icon
│   │       ├── Card.tsx                # Card with variant (outlined, interactive)
│   │       ├── Input.tsx               # Text input with optional label, error, left/right icon
│   │       ├── Modal.tsx               # Modal with title, close, size
│   │       └── index.ts               # Re-exports neo components
│   ├── contexts/
│   │   └── AuthContext.tsx             # Provides user, signUp, signIn, logout, refreshUser; restores from localStorage
│   ├── index.css                       # Global styles
│   ├── lib/
│   │   └── utils.ts                   # cn() for class names (clsx + tailwind-merge)
│   ├── main.tsx                       # React root, StrictMode, App
│   ├── pages/
│   │   ├── DashboardNeo.tsx           # Dashboard: on load GET profile → curated search or banner; semantic search; detail modal; Generate Email → redirect to /outreach
│   │   ├── OutreachEmail.tsx          # Full-page email draft (state: subject, body, opportunity_title, pi_name, institution); Copy, Send via Gmail (disabled)
│   │   ├── Profile.tsx               # Profile edit + Upload Resume (PDF, Upload & Parse → auto-fill research_interests, PATCH)
│   │   ├── SignIn.tsx                 # Sign-in form, redirect to dashboard
│   │   └── SignUp.tsx                 # Sign-up form, validation, redirect to dashboard
│   ├── services/
│   │   ├── auth.ts                    # Axios instance (JWT interceptors; drops Content-Type for FormData so multipart works), AuthService, TokenStorage
│   │   ├── opportunities.ts           # getOpportunities, getOpportunity, create, update, delete
│   │   └── profile.ts                 # getProfile, updateProfile (PATCH), uploadResume(file) multipart
│   ├── styles/
│   │   └── tokens.ts                  # Design tokens (colors, shadows, etc.)
│   └── utils/
│       └── apiError.ts                # formatApiErrorDetail() for FastAPI 422/400 response bodies
├── tailwind.config.js
├── tsconfig.app.json
├── tsconfig.json
├── tsconfig.node.json
└── vite.config.ts                      # Vite + React plugin, path alias @
```

---

## Backend — what's fully working

- **GET /** — Root; returns `{ message, status, version, docs }`.
- **GET /health** — Health check; returns `{ status: "healthy", service, version }`.
- **POST /api/auth/signup** — Register; body `email`, `password`, `name`. Validates password (8+ chars, upper, lower, digit). Returns `AuthResponse` (user, access_token, refresh_token, token_type, expires_in). Creates user and refresh_token row.
- **POST /api/auth/signin** — Login; body `email`, `password`. Returns same `AuthResponse`. Creates refresh_token row.
- **POST /api/auth/refresh** — Body `refresh_token`. Returns new `TokenPair`; revokes old refresh token.
- **POST /api/auth/logout** — Body `refresh_token`; requires Bearer. Revokes the given refresh token.
- **GET /api/auth/me** — Requires Bearer. Returns current user (user_id, email, name, created_at).
- **GET /api/opportunities** — List opportunities. Query params: skip, limit, is_active, search (ILIKE title/description/lab/pi), institution, funding_status. Returns list of `OpportunityResponse`. Auth not required for list (no Depends(get_current_user)).
- **GET /api/opportunities/{opportunity_id}** — Get one opportunity. Returns `OpportunityResponse`.
- **POST /api/opportunities** — Create opportunity; requires Bearer. Body: full opportunity fields. Returns created `OpportunityResponse`.
- **PUT /api/opportunities/{opportunity_id}** — Update; requires Bearer. Returns updated `OpportunityResponse`.
- **DELETE /api/opportunities/{opportunity_id}** — Soft delete (sets is_active=false); requires Bearer. Returns 204.
- **POST /api/opportunities/search** — Semantic search. No auth. Body: `query` (min 10 chars), optional `filters`, `limit`. Uses pgvector when available; on SQLite/Postgres without pgvector falls back to numpy cosine similarity (embeds query + each opportunity on the fly). Returns `SearchResponse` (query, results with similarity_score, count, total_opportunities). Requires `OPENAI_API_KEY`.
- **GET /api/opportunities/search/test** — Returns embedding counts / search setup info; no auth.
- **GET /api/profile** — Current user profile; requires Bearer. Returns `ProfileResponse` (all profile fields).
- **POST /api/profile** — Full profile create/update; requires Bearer. Body: `ProfileCreate` (university, major, graduation_year, research_interests, etc.). Returns `ProfileResponse`.
- **PATCH /api/profile** — Partial update; requires Bearer. Body: `ProfileUpdate` (all optional). Returns `ProfileResponse`.
- **GET /api/profile/{user_id}** — Get another user's profile; requires Bearer. Returns `ProfileResponse`.
- **POST /api/profile/upload-resume** — Upload PDF; requires Bearer. Saves file, parses (skills, education, GPT-4o research_summary, raw_text). Auto-updates user profile: research_interests=research_summary, university/major/graduation_year from education (PATCH-style, only non-null). Returns full parsed_data (skills, education, research_summary, raw_text) + file_path. Max 10MB. Requires OPENAI_API_KEY for research_summary.
- **POST /api/outreach/generate** — Generate cold email; requires Bearer. Body: `opportunity_id`, optional `additional_context`. Uses `research_interests` as student background (narrative from resume or manual). Prompt: professor/lab details (PI, lab, institution, research topics, description), 150–200 words, specific connection + 1–2 projects, subject/body format; response parsed to split subject and body. Saves Outreach, returns `{ subject, body, opportunity_id, outreach_id }`. Requires `OPENAI_API_KEY`.
- **POST /api/scrape/run** — Triggers `run_ucla_scrape()` (no auth). Returns `{ status, opportunities_added }`. Scraper: research-labs page → professor names → DuckDuckGo/page URLs → fetch + GPT-4o extraction → insert opportunities + generate embeddings per opportunity. Blocks until done.

---

## Backend — what's partially working or broken

- **Embeddings (SQLite)** — `init_db()` only creates tables for User, Opportunity, Match, Outreach, RefreshToken. It does **not** create `user_embeddings` or `opportunity_embeddings` (they use pgvector/Vector in migrations). On a fresh SQLite setup, **POST /api/embeddings/users/{user_id}**, **POST /api/embeddings/opportunities/{opportunity_id}**, **POST .../generate-all**, and **GET /api/embeddings/stats** will fail with “no such table” (or similar). **Semantic search** still works on SQLite because the search router catches pgvector/DB errors and uses an in-memory numpy fallback (embeds query and each opportunity on the fly; no stored embeddings).
- **Embeddings (PostgreSQL)** — Full embedding and vector search work only after running `alembic upgrade head` so that embedding tables exist and use pgvector.
- **Search** — Depends on `OPENAI_API_KEY`. Without it, search returns 503 or similar. With SQLite, search does not use stored embeddings; it embeds every opportunity per request (slower, but works).
- **Outreach generate** — Returns 400 if the user’s profile has no `research_interests`. Returns 503 if `OPENAI_API_KEY` is missing.
- **Scrape /run** — No auth; long-running. If the server is not run from the backend directory, the scraper module may not import and the endpoint returns “Scraper not available”.
- **reset_db** — In `database.py`, `reset_db()` imports `from app.models import User, Opportunity, Match, Outreach` and does **not** include RefreshToken; so after reset, auth tables may be missing until init_db is run again (init_db creates all tables including refresh_tokens). Typically you’d run init_db after a reset for a clean state.

---

## Frontend — what's fully working

- **Routing** — `/signup`, `/signin`, `/dashboard`, `/profile`, `/outreach`, `/` → dashboard. Protected routes redirect to `/signin` when not authenticated.
- **Auth** — SignUp and SignIn forms with validation. Tokens stored in localStorage. Axios request interceptor adds Bearer token; response interceptor refreshes token on 401 and retries. Logout clears storage and calls logout API.
- **SignUp page** — Name, email, password, confirm password. Client-side validation; backend validation errors (including 422 detail array) and network errors surfaced via `formatApiErrorDetail`.
- **SignIn page** — Email, password. Redirect to dashboard on success.
- **Dashboard (DashboardNeo)** — Nav: “Research Assistant”, Profile link, Welcome + name, Logout. **On load:** GET /api/profile (auth); if `research_interests` set and non-empty, POST /api/opportunities/search with that query (limit 10) and show results with “X% match” and label “Curated for your profile”; else GET /api/opportunities and show banner “Upload your resume on the Profile page to get personalized results”. Manual semantic search: text input + Search button (min 10 chars) → POST /api/opportunities/search → replaces list with “X% match” badges. Clear + Search restores default list. Loading state. Error/empty states. Opportunity cards; detail modal with full description, topics, methods, deadline, funding, contact, Apply Now / View Source; “Generate Email” → POST /api/outreach/generate → redirect to /outreach with email state (“Generating...” on button).
- **Outreach email page (/outreach)** — Full-page draft; receives state via router (subject, body, opportunity_title, pi_name, institution). Header “Your Email Draft”, back to dashboard. Card: To / Re, subject in bold, body in pre-wrap. Copy to Clipboard (shows “Copied!” 2s), Send via Gmail disabled with tooltip “Coming soon”. Redirects to /dashboard if state missing.
- **Profile page** — GET /api/profile on load. **Upload Resume:** file input (accept .pdf), “Upload & Parse” → POST /api/profile/upload-resume (multipart, auth); on success backend auto-updates profile; frontend fills form from `parsed_data.research_summary` and `parsed_data.education`, sets read-only skills from `parsed_data.skills` (Neo Badges), refetches profile, shows “Resume parsed — research summary and education auto-filled. Review and save.” No auto-save; user reviews and clicks Save. Form: name, research_interests, university, major, graduation_year, experience_level; **Skills (from resume)** read-only badges (from profile on load or latest parse). Save → PATCH. Nav: Dashboard, Logout.
- **ProtectedRoute** — Reads auth from context; redirects to /signin if not authenticated.
- **Neo components** — Card, Button, Badge, Input, Modal. Input has bg-white, text-gray-900, placeholder-gray-500 for visibility.
- **Services** — auth (api with JWT + FormData Content-Type drop for multipart), opportunities (CRUD), profile (getProfile, updateProfile, uploadResume).

---

## Frontend — what's missing or incomplete

- **Matches / recommendations** — No “My Matches” or recommendation UI. Backend has Match model but no matches API or scoring UI.
- **Profile** — No display of past_experiences or publications in the form. Skills are read-only badges (from profile or latest resume parse); research_interests and education are editable and auto-filled from resume.
- **Filters on search** — Semantic search supports filters (states, degree_level, is_remote, etc.); Dashboard search form does not expose filter UI (sends only query and limit).
- **Opportunity create/edit/delete** — Backend supports create, update, delete; frontend has no admin or CRUD UI for opportunities (only list, detail, generate email).
- **Embeddings UI** — No UI to trigger “generate my embedding” or “generate all opportunity embeddings”; only backend/scripts or API calls.

---

## Data flow

- **Sign up** — User submits form → POST /api/auth/signup → backend creates User + RefreshToken → returns tokens + user → frontend stores tokens and user in localStorage and AuthContext → redirect to /dashboard.
- **Sign in** — Same flow with POST /api/auth/signin; tokens and user stored; redirect to /dashboard.
- **Load dashboard** — ProtectedRoute checks auth → GET /api/profile with Bearer → if `research_interests` set (≥10 chars), POST /api/opportunities/search { query: research_interests, limit: 10 } (plain fetch) → show results with “X% match” and “Curated for your profile”; else GET /api/opportunities and show list + banner “Upload your resume on the Profile page to get personalized results”.
- **Semantic search (manual)** — User enters query, clicks Search → POST /api/opportunities/search { query, limit: 10 } → frontend replaces list with results and “X% match” badges. Clear + Search restores default list.
- **Generate email** — User opens opportunity modal, clicks Generate Email → POST /api/outreach/generate with Bearer → backend saves Outreach, returns subject/body/opportunity_id/outreach_id → frontend navigates to /outreach with state (subject, body, opportunity_title, pi_name, institution). Outreach page shows draft, Copy to Clipboard, Send via Gmail (disabled, “Coming soon”).
- **Profile save** — User edits form on /profile, Save → PATCH /api/profile with Bearer → frontend shows “Profile saved.”
- **Resume upload** — User selects PDF on /profile, clicks Upload & Parse → POST /api/profile/upload-resume (multipart, Bearer; axios drops Content-Type so multipart boundary is set) → backend saves file, parses (skills, education, GPT-4o research_summary, raw_text), auto-updates profile (research_interests, university, major, graduation_year), returns full parsed_data → frontend can refetch profile or fill form from response; user reviews and clicks Save → “Resume parsed and profile updated!”
- **Auth refresh** — Any authed request that returns 401 → interceptor calls POST /api/auth/refresh → new tokens, retry; else clear storage and redirect to /signin.

---

## Known issues or TODOs

- **Profile incomplete message** — Outreach generate returns 400 with “Profile incomplete: add your research interests…” when `research_interests` is empty; user must use Profile page to set it. Documented in code and README.
- **SQLite vs PostgreSQL** — init_db is SQLite-safe (no Vector/ARRAY). Embedding tables and vector search require PostgreSQL + alembic migrations. Semantic search on SQLite works via numpy fallback but does not use stored embeddings.
- **Scraper** — Run from backend directory so `scrape_ucla` imports. Long-running; no auth on POST /api/scrape/run.
- **CORS** — Backend allows localhost:3000, 5173, 5174, 127.0.0.1:5173, 5174. Other origins need to be added in config.
- **Secrets** — Default SECRET_KEY in config; production should set env. OPENAI_API_KEY required for search and outreach (and embeddings when used).
- **No matches API** — Match model exists; no endpoints to compute or return matches for a user.
- **Scraper title/lab** — scrape_ucla GPT prompt uses “Professor” (and “Professor Lab”) when last name cannot be determined.
